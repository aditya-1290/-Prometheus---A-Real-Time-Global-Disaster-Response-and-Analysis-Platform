from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Base settings for all services"""
    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Service-specific settings can be added in child classes
    
    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    """Create and cache settings instance"""
    return Settings()
