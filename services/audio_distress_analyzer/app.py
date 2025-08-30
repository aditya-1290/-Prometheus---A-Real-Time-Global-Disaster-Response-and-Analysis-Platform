from flask import Flask, request, jsonify
from shared.event_producer import EventProducer
from shared.config import Settings, get_settings
from shared.ml_utils import AudioProcessor, ModelManager
import torch
import torch.nn as nn
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2Processor
import numpy as np
from typing import List, Dict, Any
from kafka import KafkaConsumer
import json
import threading
import librosa

class DistressAnalyzer(ModelManager):
    def __init__(self, model_path: str = "facebook/wav2vec2-base"):
        super().__init__(model_path)
        self.processor = None
        self.load_model()
        self.emotion_labels = [
            'neutral',
            'distressed',
            'panicked',
            'urgent'
        ]
    
    def load_model(self):
        """Load the audio analysis model"""
        self.processor = Wav2Vec2Processor.from_pretrained(self.model_path)
        self.model = Wav2Vec2ForSequenceClassification.from_pretrained(
            self.model_path,
            num_labels=len(self.emotion_labels)
        )
        # TODO: Load fine-tuned weights when available
        self.model.to(self.device)
    
    def preprocess(self, audio_samples: List[np.ndarray]) -> torch.Tensor:
        """Preprocess audio samples"""
        inputs = self.processor(
            audio_samples,
            sampling_rate=16000,
            padding=True,
            return_tensors="pt"
        )
        return inputs.input_values.to(self.device)
    
    def predict(self, inputs: torch.Tensor) -> torch.Tensor:
        """Make predictions"""
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(inputs)
            return torch.softmax(outputs.logits, dim=1)
    
    def postprocess(self, predictions: torch.Tensor) -> List[Dict[str, Any]]:
        """Postprocess predictions"""
        predictions = predictions.cpu().numpy()
        results = []
        
        for pred in predictions:
            emotion_probs = {
                label: float(prob)
                for label, prob in zip(self.emotion_labels, pred)
            }
            
            # Calculate distress level
            distress_level = (
                emotion_probs['distressed'] +
                2 * emotion_probs['panicked'] +
                1.5 * emotion_probs['urgent']
            ) / 4.5  # Normalize to [0, 1]
            
            results.append({
                'emotions': emotion_probs,
                'distress_level': float(distress_level),
                'requires_immediate_response': bool(distress_level > 0.6),
                'priority_level': 'high' if distress_level > 0.6 else 'medium' if distress_level > 0.3 else 'low'
            })
        
        return results

app = Flask(__name__)
settings = get_settings()
event_producer = EventProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
analyzer = DistressAnalyzer()

def start_kafka_consumer():
    """Start consuming messages from Kafka"""
    consumer = KafkaConsumer(
        'news_transcripts',
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    for message in consumer:
        process_message(message.value)

def process_audio(audio_data: bytes, sample_rate: int = 16000) -> np.ndarray:
    """Process raw audio data"""
    # Convert audio to mono and resample if needed
    audio, sr = librosa.load(audio_data, sr=sample_rate, mono=True)
    return audio

def process_message(message: Dict[str, Any]):
    """Process incoming audio transcripts"""
    try:
        # Process audio if available
        if 'audio_url' in message:
            # TODO: Implement audio downloading and processing
            pass
        
        # Process transcript text for distress indicators
        if 'text' in message:
            # TODO: Implement text-based distress analysis
            pass
        
        # Add results to message
        message['distress_analysis'] = {
            'distress_level': 0.0,  # Placeholder
            'priority_level': 'low'
        }
        
        # Emit processed message
        event_producer.emit_event('distress_analyses', message)
    except Exception as e:
        print(f"Error processing message: {str(e)}")

@app.route('/api/analyze', methods=['POST'])
def analyze_audio():
    """Endpoint for analyzing audio directly"""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    try:
        audio_file = request.files['audio']
        audio_data = process_audio(audio_file)
        
        inputs = analyzer.preprocess([audio_data])
        predictions = analyzer.predict(inputs)
        results = analyzer.postprocess(predictions)
        
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
    app.run(port=5004)
