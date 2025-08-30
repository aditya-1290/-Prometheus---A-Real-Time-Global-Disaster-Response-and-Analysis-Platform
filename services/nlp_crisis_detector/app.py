from flask import Flask, request, jsonify
from shared.event_producer import EventProducer
from shared.config import Settings, get_settings
from shared.ml_utils import TextProcessor, ModelManager
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from typing import List, Dict, Any
from kafka import KafkaConsumer
import json
import threading

class CrisisClassifier(ModelManager):
    def __init__(self, model_path: str = "facebook/bart-large-mnli"):
        super().__init__(model_path)
        self.tokenizer = None
        self.load_model()
    
    def load_model(self):
        """Load the crisis classification model"""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
        self.model.to(self.device)
    
    def preprocess(self, texts: List[str]) -> Dict[str, torch.Tensor]:
        """Preprocess input texts"""
        return self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )
    
    def predict(self, inputs: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Make predictions"""
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
            return torch.softmax(outputs.logits, dim=1)
    
    def postprocess(self, predictions: torch.Tensor) -> List[Dict[str, Any]]:
        """Postprocess predictions"""
        predictions = predictions.cpu().numpy()
        return [
            {
                "crisis_probability": float(pred[1]),
                "is_crisis": bool(pred[1] > 0.5)
            }
            for pred in predictions
        ]

app = Flask(__name__)
settings = get_settings()
event_producer = EventProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
classifier = CrisisClassifier()

def start_kafka_consumer():
    """Start consuming messages from Kafka"""
    consumer = KafkaConsumer(
        'raw_social_media_messages',
        'news_transcripts',
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    for message in consumer:
        process_message(message.value)

def process_message(message: Dict[str, Any]):
    """Process incoming messages and emit results"""
    try:
        # Extract text based on message type
        text = message.get('content', message.get('text', ''))
        
        # Classify text
        inputs = classifier.preprocess([text])
        predictions = classifier.predict(inputs)
        results = classifier.postprocess(predictions)[0]
        
        # Add results to message
        message['crisis_detection'] = results
        
        # Emit processed message
        event_producer.emit_event('crisis_detections', message)
    except Exception as e:
        print(f"Error processing message: {str(e)}")

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """Endpoint for analyzing text directly"""
    data = request.get_json()
    texts = data.get('texts', [])
    
    if not texts:
        return jsonify({'error': 'No texts provided'}), 400
    
    try:
        inputs = classifier.preprocess(texts)
        predictions = classifier.predict(inputs)
        results = classifier.postprocess(predictions)
        
        return jsonify({
            'results': results,
            'count': len(results)
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
    app.run(port=5000)
