from flask import Flask, request, jsonify
from shared.event_producer import EventProducer
from shared.config import Settings, get_settings
from shared.ml_utils import ImageProcessor, ModelManager
import torch
import torch.nn as nn
import torchvision.models as models
import segmentation_models_pytorch as smp
import numpy as np
from typing import List, Dict, Any
from kafka import KafkaConsumer
import json
import threading
import requests
from io import BytesIO
from PIL import Image

class FloodDetector(ModelManager):
    def __init__(self, model_path: str = None):
        super().__init__(model_path)
        self.load_model()
    
    def load_model(self):
        """Load the flood detection model"""
        # Using U-Net with ResNet34 encoder for segmentation
        self.model = smp.Unet(
            encoder_name="resnet34",
            encoder_weights="imagenet",
            in_channels=3,
            classes=1,  # Binary segmentation
        )
        # TODO: Load trained weights when available
        self.model.to(self.device)
    
    def preprocess(self, images: List[np.ndarray]) -> torch.Tensor:
        """Preprocess input images"""
        processed = []
        for img in images:
            if len(img.shape) == 3:
                img = np.expand_dims(img, 0)
            processed.append(img)
        return torch.FloatTensor(np.concatenate(processed)).to(self.device)
    
    def predict(self, inputs: torch.Tensor) -> torch.Tensor:
        """Make predictions"""
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(inputs)
            return torch.sigmoid(outputs)
    
    def postprocess(self, predictions: torch.Tensor) -> List[Dict[str, Any]]:
        """Postprocess predictions"""
        predictions = predictions.cpu().numpy()
        results = []
        
        for pred in predictions:
            # Calculate flood extent
            flood_mask = (pred[0] > 0.5).astype(np.uint8)
            flood_percentage = np.mean(flood_mask) * 100
            
            results.append({
                "flood_percentage": float(flood_percentage),
                "has_flooding": bool(flood_percentage > 1.0),  # More than 1% coverage
                "severity": "high" if flood_percentage > 30 else "medium" if flood_percentage > 10 else "low"
            })
        
        return results

app = Flask(__name__)
settings = get_settings()
event_producer = EventProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
detector = FloodDetector()
image_processor = ImageProcessor()

def start_kafka_consumer():
    """Start consuming messages from Kafka"""
    consumer = KafkaConsumer(
        'raw_satellite_images',
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    for message in consumer:
        process_message(message.value)

def download_image(url: str) -> np.ndarray:
    """Download and preprocess image from URL"""
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return ImageProcessor.load_image(img)

def process_message(message: Dict[str, Any]):
    """Process incoming satellite images"""
    try:
        # Download and process image
        image_url = message.get('download_url')
        if not image_url:
            return
        
        img = download_image(image_url)
        inputs = detector.preprocess([img])
        predictions = detector.predict(inputs)
        results = detector.postprocess(predictions)[0]
        
        # Add results to message
        message['flood_detection'] = results
        
        # Emit processed message
        event_producer.emit_event('flood_detections', message)
    except Exception as e:
        print(f"Error processing message: {str(e)}")

@app.route('/api/detect', methods=['POST'])
def detect_flood():
    """Endpoint for analyzing images directly"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    try:
        image_file = request.files['image']
        img = Image.open(image_file)
        img_array = ImageProcessor.load_image(img)
        
        inputs = detector.preprocess([img_array])
        predictions = detector.predict(inputs)
        results = detector.postprocess(predictions)
        
        return jsonify({
            'results': results[0]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Start Kafka consumer in a separate thread
    consumer_thread = threading.Thread(target=start_kafka_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()
    
    # Start Flask app
    app.run(port=5002)
