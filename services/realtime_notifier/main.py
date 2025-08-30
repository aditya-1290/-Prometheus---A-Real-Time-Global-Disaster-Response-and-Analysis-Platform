from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Dict, List, Set, Optional
from datetime import datetime
import json
import asyncio
import aioredis
import httpx
from aiokafka import AIOKafkaConsumer
from shared.config import Settings, get_settings

app = FastAPI(title="Prometheus Real-time Notifier")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Subscription(BaseModel):
    user_id: str
    event_types: List[str]
    regions: List[Dict[str, float]]  # List of bounding boxes
    severity_threshold: str
    notification_channels: List[str]

class Notification(BaseModel):
    id: str
    type: str
    title: str
    message: str
    severity: str
    timestamp: datetime
    data: Optional[Dict] = None

# Global state
class NotificationManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.user_subscriptions: Dict[str, Subscription] = {}
        self.redis: Optional[aioredis.Redis] = None
        self.kafka_consumer: Optional[AIOKafkaConsumer] = None
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
    
    async def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections[user_id].remove(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]
    
    async def broadcast_to_user(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    await self.disconnect(connection, user_id)
    
    async def start_kafka_consumer(self):
        """Start consuming Kafka topics"""
        topics = [
            'crisis_detections',
            'wildfire_detections',
            'flood_detections',
            'damage_assessments',
            'distress_analyses'
        ]
        
        self.kafka_consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers='localhost:9092',
            group_id='notifier_group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        await self.kafka_consumer.start()
        
        try:
            async for msg in self.kafka_consumer:
                await self.process_event(msg.topic, msg.value)
        finally:
            await self.kafka_consumer.stop()
    
    async def process_event(self, topic: str, event: dict):
        """Process incoming events and notify relevant subscribers"""
        notification = self.create_notification(topic, event)
        
        # Find relevant subscribers
        for user_id, subscription in self.user_subscriptions.items():
            if self.should_notify(subscription, notification):
                # Store notification in Redis
                await self.store_notification(user_id, notification)
                
                # Send real-time notification if user is connected
                await self.broadcast_to_user(user_id, notification.dict())
                
                # Send notifications through other channels
                await self.send_external_notifications(user_id, notification, subscription)
    
    def create_notification(self, topic: str, event: dict) -> Notification:
        """Create a notification from an event"""
        return Notification(
            id=str(event.get('id', '')),
            type=topic,
            title=f"New {topic.replace('_', ' ')} detected",
            message=self.create_message(topic, event),
            severity=event.get('severity', 'medium'),
            timestamp=datetime.now(),
            data=event
        )
    
    def create_message(self, topic: str, event: dict) -> str:
        """Create a human-readable message from an event"""
        if topic == 'crisis_detections':
            return f"Crisis detected: {event.get('description', 'No description')}"
        elif topic == 'wildfire_detections':
            return f"Wildfire detected with {event.get('confidence', 0)}% confidence"
        elif topic == 'flood_detections':
            return f"Flood detected covering {event.get('area_affected', 0)} sq km"
        elif topic == 'damage_assessments':
            return f"Damage assessment completed: {event.get('summary', 'No summary')}"
        else:
            return f"New event detected in {topic}"
    
    def should_notify(self, subscription: Subscription, notification: Notification) -> bool:
        """Check if a subscriber should receive a notification"""
        # Check event type
        if notification.type not in subscription.event_types:
            return False
        
        # Check severity threshold
        severity_levels = ['low', 'medium', 'high', 'critical']
        if (severity_levels.index(notification.severity) <
            severity_levels.index(subscription.severity_threshold)):
            return False
        
        # Check region (if applicable and if event has location data)
        if subscription.regions and notification.data.get('location'):
            loc = notification.data['location']
            in_region = False
            for region in subscription.regions:
                if (region['min_lat'] <= loc['lat'] <= region['max_lat'] and
                    region['min_lon'] <= loc['lon'] <= region['max_lon']):
                    in_region = True
                    break
            if not in_region:
                return False
        
        return True
    
    async def store_notification(self, user_id: str, notification: Notification):
        """Store notification in Redis"""
        if self.redis:
            key = f"notifications:{user_id}"
            await self.redis.lpush(key, notification.json())
            await self.redis.ltrim(key, 0, 99)  # Keep last 100 notifications
    
    async def send_external_notifications(
        self,
        user_id: str,
        notification: Notification,
        subscription: Subscription
    ):
        """Send notifications through external channels"""
        for channel in subscription.notification_channels:
            if channel == 'email':
                await self.send_email_notification(user_id, notification)
            elif channel == 'sms':
                await self.send_sms_notification(user_id, notification)
    
    async def send_email_notification(self, user_id: str, notification: Notification):
        """Send email notification"""
        # TODO: Implement email sending
        pass
    
    async def send_sms_notification(self, user_id: str, notification: Notification):
        """Send SMS notification"""
        # TODO: Implement SMS sending
        pass

# Initialize notification manager
manager = NotificationManager()

@app.on_event("startup")
async def startup_event():
    """Initialize Redis and start Kafka consumer"""
    manager.redis = await aioredis.create_redis_pool('redis://localhost')
    asyncio.create_task(manager.start_kafka_consumer())

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources"""
    if manager.redis:
        manager.redis.close()
        await manager.redis.wait_closed()
    if manager.kafka_consumer:
        await manager.kafka_consumer.stop()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time notifications"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)

@app.post("/subscribe")
async def subscribe(subscription: Subscription):
    """Subscribe to notifications"""
    manager.user_subscriptions[subscription.user_id] = subscription
    return {"status": "subscribed"}

@app.delete("/unsubscribe/{user_id}")
async def unsubscribe(user_id: str):
    """Unsubscribe from notifications"""
    if user_id in manager.user_subscriptions:
        del manager.user_subscriptions[user_id]
    return {"status": "unsubscribed"}

@app.get("/notifications/{user_id}")
async def get_notifications(user_id: str, limit: int = 50):
    """Get recent notifications for a user"""
    if manager.redis:
        key = f"notifications:{user_id}"
        notifications = await manager.redis.lrange(key, 0, limit - 1)
        return [json.loads(n) for n in notifications]
    return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001)
