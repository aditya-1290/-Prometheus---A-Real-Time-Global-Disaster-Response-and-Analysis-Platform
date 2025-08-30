from fastapi import FastAPI, WebSocket
from shared.event_producer import EventProducer
from shared.config import Settings, get_settings
from pydantic import BaseModel
from typing import Optional, List
import json

class SocialMediaMessage(BaseModel):
    """Base model for social media messages"""
    platform: str
    content: str
    timestamp: str
    location: Optional[dict] = None
    author: str
    hashtags: List[str] = []
    media_urls: List[str] = []
    metadata: dict = {}

app = FastAPI(title="Social Media Ingestor Service")
settings = get_settings()
event_producer = EventProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)

@app.on_event("startup")
async def startup_event():
    """Initialize Kafka producer on startup"""
    await event_producer.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up Kafka producer on shutdown"""
    await event_producer.stop()

@app.websocket("/ws/social-feed")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time social media feed"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = SocialMediaMessage.parse_raw(data)
            
            # Emit event to Kafka
            await event_producer.emit_event(
                "raw_social_media_messages",
                message.dict()
            )
            
            # Acknowledge receipt
            await websocket.send_text(json.dumps({"status": "received"}))
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
    finally:
        await websocket.close()

@app.post("/api/social-media/batch")
async def process_batch(messages: List[SocialMediaMessage]):
    """Endpoint for batch processing of social media messages"""
    for message in messages:
        await event_producer.emit_event(
            "raw_social_media_messages",
            message.dict()
        )
    return {"status": "success", "processed": len(messages)}
