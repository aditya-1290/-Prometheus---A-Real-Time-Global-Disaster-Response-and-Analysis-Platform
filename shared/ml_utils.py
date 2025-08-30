from typing import Any, Dict, List
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from PIL import Image
import tensorflow as tf

class ModelManager:
    """Base class for managing ML models"""
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def load_model(self):
        """Load model implementation - to be overridden"""
        raise NotImplementedError
    
    def preprocess(self, input_data: Any) -> Any:
        """Preprocess input data - to be overridden"""
        raise NotImplementedError
    
    def predict(self, input_data: Any) -> Any:
        """Make predictions - to be overridden"""
        raise NotImplementedError
    
    def postprocess(self, predictions: Any) -> Dict[str, Any]:
        """Postprocess predictions - to be overridden"""
        raise NotImplementedError

class TextProcessor:
    """Text processing utilities"""
    def __init__(self, model_name: str = "bert-base-uncased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get BERT embeddings for a list of texts"""
        encoded = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        encoded = {k: v.to(self.device) for k, v in encoded.items()}
        
        with torch.no_grad():
            outputs = self.model(**encoded)
            embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        
        return embeddings

class ImageProcessor:
    """Image processing utilities"""
    @staticmethod
    def load_image(image_path: str, target_size: tuple = (224, 224)) -> np.ndarray:
        """Load and preprocess an image"""
        img = Image.open(image_path)
        img = img.resize(target_size)
        img_array = np.array(img) / 255.0
        return img_array
    
    @staticmethod
    def batch_process_images(image_paths: List[str], target_size: tuple = (224, 224)) -> np.ndarray:
        """Process multiple images"""
        images = []
        for path in image_paths:
            img = ImageProcessor.load_image(path, target_size)
            images.append(img)
        return np.array(images)

class AudioProcessor:
    """Audio processing utilities for processing and feature extraction from audio files"""
    
    @staticmethod
    def load_audio(audio_path: str, sample_rate: int = 16000) -> np.ndarray:
        """
        Load and preprocess audio file with resampling and normalization
        
        Args:
            audio_path: Path to the audio file
            sample_rate: Target sample rate for the audio
            
        Returns:
            Preprocessed audio signal as numpy array
        """
        import librosa
        
        # Load audio file with resampling
        audio, _ = librosa.load(audio_path, sr=sample_rate, mono=True)
        
        # Apply preprocessing
        # 1. Trim silence
        audio, _ = librosa.effects.trim(audio, top_db=20)
        
        # 2. Normalize audio
        audio = librosa.util.normalize(audio)
        
        # 3. Ensure consistent length (pad or trim to 30 seconds)
        target_length = 30 * sample_rate
        if len(audio) < target_length:
            # Pad with zeros if too short
            audio = np.pad(audio, (0, target_length - len(audio)))
        else:
            # Trim if too long
            audio = audio[:target_length]
            
        return audio
    
    @staticmethod
    def extract_features(audio: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
        """
        Extract audio features including MFCCs, spectral features, and rhythm features
        
        Args:
            audio: Input audio signal
            sample_rate: Sample rate of the audio signal
            
        Returns:
            Feature matrix containing extracted features
        """
        import librosa
        
        features = []
        
        # 1. Extract MFCCs (Mel-frequency cepstral coefficients)
        mfccs = librosa.feature.mfcc(
            y=audio, 
            sr=sample_rate,
            n_mfcc=13,  # Number of MFCCs to compute
            hop_length=512
        )
        mfccs_mean = np.mean(mfccs, axis=1)
        mfccs_var = np.var(mfccs, axis=1)
        features.extend(mfccs_mean)
        features.extend(mfccs_var)
        
        # 2. Spectral features
        # Spectral centroid
        spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)
        features.append(np.mean(spectral_centroids))
        
        # Spectral rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sample_rate)
        features.append(np.mean(spectral_rolloff))
        
        # Spectral bandwidth
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate)
        features.append(np.mean(spectral_bandwidth))
        
        # 3. Rhythm features
        # Tempo
        tempo, _ = librosa.beat.beat_track(y=audio, sr=sample_rate)
        features.append(tempo)
        
        # Zero crossing rate
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)
        features.append(np.mean(zero_crossing_rate))
        
        # 4. Root Mean Square Energy
        rms = librosa.feature.rms(y=audio)
        features.append(np.mean(rms))
        
        return np.array(features)
