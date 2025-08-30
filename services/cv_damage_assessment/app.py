from flask import Flask, request, jsonify
from shared.event_producer import EventProducer
from shared.config import Settings, get_settings
from shared.ml_utils import ImageProcessor, ModelManager
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.models.detection as detection
import numpy as np
from typing import List, Dict, Any
from kafka import KafkaConsumer
import json
import threading
import requests
from io import BytesIO
from PIL import Image

class DamageDetector(ModelManager):
    def __init__(self, model_path: str = None):
        super().__init__(model_path)
        self.load_model()
        self.classes = [
            'building_damage',
            'road_blockage',
            'flood_damage',
            'fire_damage',
            'debris',
            'temporary_shelter'
        ]
    
    def load_model(self):
        """Load the damage detection model"""
        # Using Faster R-CNN with ResNet50 backbone
        self.model = detection.fasterrcnn_resnet50_fpn(
            pretrained=True,
            num_classes=len(self.classes) + 1  # +1 for background
        )
        # TODO: Load trained weights when available
        self.model.to(self.device)
    
    def preprocess(self, images: List[np.ndarray]) -> List[torch.Tensor]:
        """Preprocess input images"""
        processed = []
        for img in images:
            # Convert to torch tensor and normalize
            img_tensor = torch.from_numpy(img.transpose(2, 0, 1)).float()
            img_tensor = img_tensor / 255.0
            processed.append(img_tensor.to(self.device))
        return processed
    
    def predict(self, inputs: List[torch.Tensor]) -> List[Dict[str, torch.Tensor]]:
        """Make predictions"""
        self.model.eval()
        with torch.no_grad():
            predictions = self.model(inputs)
        return predictions
    
    def postprocess(self, predictions: List[Dict[str, torch.Tensor]]) -> List[Dict[str, Any]]:
        """Postprocess predictions"""
        results = []
        for pred in predictions:
            boxes = pred['boxes'].cpu().numpy()
            scores = pred['scores'].cpu().numpy()
            labels = pred['labels'].cpu().numpy()
            
            # Filter predictions by confidence threshold
            mask = scores > 0.5
            boxes = boxes[mask]
            scores = scores[mask]
            labels = labels[mask]
            
            # Format detections
            detections = []
            for box, score, label in zip(boxes, scores, labels):
                detections.append({
                    'category': self.classes[label - 1],
                    'confidence': float(score),
                    'bbox': box.tolist()
                })
            
            # Calculate damage assessment metrics
            damage_metrics = self._calculate_damage_metrics(detections)
            
            results.append({
                'detections': detections,
                'damage_assessment': damage_metrics
            })
        
        return results
    
    def _calculate_damage_metrics(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate damage assessment metrics"""
        metrics = {
            'total_damaged_buildings': 0,
            'total_blocked_roads': 0,
            'total_temporary_shelters': 0,
            'damage_severity': 'low'
        }
        
        for det in detections:
            if det['category'] == 'building_damage':
                metrics['total_damaged_buildings'] += 1
            elif det['category'] == 'road_blockage':
                metrics['total_blocked_roads'] += 1
            elif det['category'] == 'temporary_shelter':
                metrics['total_temporary_shelters'] += 1
        
        # Determine overall severity
        if metrics['total_damaged_buildings'] > 10 or metrics['total_blocked_roads'] > 5:
            metrics['damage_severity'] = 'high'
        elif metrics['total_damaged_buildings'] > 5 or metrics['total_blocked_roads'] > 2:
            metrics['damage_severity'] = 'medium'
        
        return metrics

app = Flask(__name__)
settings = get_settings()
event_producer = EventProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
detector = DamageDetector()
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
        message['damage_assessment'] = results
        
        # Emit processed message
        event_producer.emit_event('damage_assessments', message)
    except Exception as e:
        print(f"Error processing message: {str(e)}")

@app.route('/api/assess', methods=['POST'])
def assess_damage():
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
    app.run(port=5003)
