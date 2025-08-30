from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any, Optional
import httpx
import jwt
import os
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel

app = FastAPI(title="Prometheus API Gateway")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service Registry
SERVICE_REGISTRY = {
    # Group 1: Data Ingestion Services
    "social-media": "http://localhost:8000",
    "satellite-imagery": "http://localhost:8001",
    "sensor-data": "http://localhost:8002",
    "news-radio": "http://localhost:8003",

    # Group 2: ML Processing Services
    "nlp-crisis": "http://localhost:5000",
    "cv-wildfire": "http://localhost:5001",
    "cv-flood": "http://localhost:5002",
    "cv-damage": "http://localhost:5003",
    "audio-distress": "http://localhost:5004",

    # Group 3: Analytics Services
    "event-correlation": "http://localhost:8010",
    "geospatial": "http://localhost:8011",
    "data-lake": "http://localhost:8012",

    # Group 4: Management Services
    "command-control": "http://localhost:8020",
    "realtime-notifier": "http://localhost:9001",
    "config-dashboard": "http://localhost:8022"
}

# Authentication
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    username: str
    permissions: list[str]

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(**payload)
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

# Request Tracking
async def log_request(request: Request, response: JSONResponse):
    logging.info(
        f"Request: {request.method} {request.url} - Response: {response.status_code}"
    )

# Rate Limiting
class RateLimiter:
    def __init__(self):
        self.requests = {}
        
    async def check_rate_limit(self, client_id: str, limit: int = 100):
        current_time = datetime.now()
        if client_id in self.requests:
            requests = [t for t in self.requests[client_id] 
                       if current_time - t < timedelta(minutes=1)]
            if len(requests) >= limit:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded"
                )
            self.requests[client_id] = requests + [current_time]
        else:
            self.requests[client_id] = [current_time]

rate_limiter = RateLimiter()

# Service Discovery & Health Check
async def get_service_url(service_name: str) -> str:
    if service_name not in SERVICE_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f"Service {service_name} not found"
        )
    return SERVICE_REGISTRY[service_name]

async def check_service_health(service_name: str) -> bool:
    try:
        service_url = await get_service_url(service_name)
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{service_url}/health")
            return response.status_code == 200
    except:
        return False

# Routes
@app.get("/services")
async def list_services():
    """List all available services"""
    return {
        name: {
            "url": url,
            "healthy": await check_service_health(name)
        }
        for name, url in SERVICE_REGISTRY.items()
    }

@app.get("/services/{service_name}/health")
async def service_health(service_name: str):
    """Check health of a specific service"""
    healthy = await check_service_health(service_name)
    return {"service": service_name, "healthy": healthy}

@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(
    service_name: str,
    path: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user)
):
    """Proxy requests to appropriate services"""
    # Rate limiting
    await rate_limiter.check_rate_limit(current_user.username)
    
    # Get service URL
    service_url = await get_service_url(service_name)
    
    # Forward request
    try:
        url = f"{service_url}/{path}"
        headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}
        
        # Add user context
        headers["X-User"] = current_user.username
        headers["X-Permissions"] = ",".join(current_user.permissions)
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.query_params,
                content=await request.body()
            )
            
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service unavailable")

# WebSocket support for real-time notifications
from fastapi import WebSocket
from typing import Dict, Set
import json

class NotificationManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)
        
    async def disconnect(self, websocket: WebSocket, client_id: str):
        self.active_connections[client_id].remove(websocket)
        if not self.active_connections[client_id]:
            del self.active_connections[client_id]
            
    async def broadcast(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_json(message)
                except:
                    await self.disconnect(connection, client_id)

notification_manager = NotificationManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await notification_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Process incoming WebSocket messages if needed
    except:
        await notification_manager.disconnect(websocket, client_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
