from fastapi import FastAPI, HTTPException
from shared.event_producer import EventProducer
from shared.config import Settings, get_settings
from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime

class SensorReading(BaseModel):
    """Base model for sensor readings"""
    sensor_id: str
    sensor_type: str  # e.g., "seismic", "weather", "air_quality"
    timestamp: datetime
    location: dict  # GeoJSON Point
    value: Union[float, dict]  # Single value or dictionary of values
    unit: str
    metadata: dict = {}

class SensorMetadata(BaseModel):
    """Model for sensor metadata"""
    sensor_id: str
    sensor_type: str
    location: dict
    parameters: List[str]
    update_frequency: str
    provider: str
    metadata: dict = {}

app = FastAPI(title="Sensor Data Aggregator Service")
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

@app.post("/api/sensors/readings")
async def ingest_sensor_readings(readings: List[SensorReading]):
    """Ingest sensor readings from multiple sources"""
    try:
        for reading in readings:
            await event_producer.emit_event(
                "raw_sensor_readings",
                reading.dict()
            )
        return {"status": "success", "processed": len(readings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sensors/register")
async def register_sensor(sensor: SensorMetadata):
    """Register a new sensor in the system"""
    # TODO: Implement sensor registration logic
    # This would typically involve storing sensor metadata in a database
    return {"status": "success", "sensor_id": sensor.sensor_id}

@app.get("/api/sensors/{sensor_id}/status")
async def get_sensor_status(sensor_id: str):
    """Get the current status of a sensor"""
    # TODO: Implement sensor status check
    # This would typically involve checking the last reading time
    # and the sensor's health status
    return {
        "sensor_id": sensor_id,
        "status": "active",
        "last_reading": datetime.now().isoformat(),
        "health": "good"
    }

@app.get("/api/sensors/types")
async def list_sensor_types():
    """List all available sensor types"""
    return {
        "sensor_types": [
            {
                "id": "seismic",
                "name": "Seismic Sensor",
                "parameters": ["magnitude", "depth", "intensity"]
            },
            {
                "id": "weather",
                "name": "Weather Station",
                "parameters": ["temperature", "humidity", "wind_speed", "precipitation"]
            },
            {
                "id": "air_quality",
                "name": "Air Quality Monitor",
                "parameters": ["pm2_5", "pm10", "o3", "no2", "co"]
            }
        ]
    }
