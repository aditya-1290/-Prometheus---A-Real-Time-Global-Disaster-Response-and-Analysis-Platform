from typing import Any, Dict
import json
from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

class EventProducer:
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.producer = None
        self.bootstrap_servers = bootstrap_servers

    async def start(self):
        """Start the Kafka producer"""
        if not self.producer:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await self.producer.start()

    async def stop(self):
        """Stop the Kafka producer"""
        if self.producer:
            await self.producer.stop()
            self.producer = None

    async def emit_event(self, topic: str, event_data: Dict[str, Any]):
        """
        Emit an event to a Kafka topic
        Args:
            topic: The Kafka topic to emit to
            event_data: The event data to emit
        """
        if not self.producer:
            await self.start()
        
        try:
            if isinstance(event_data, BaseModel):
                event_data = event_data.dict()
            await self.producer.send_and_wait(topic, event_data)
        except Exception as e:
            print(f"Error emitting event: {str(e)}")
            raise
