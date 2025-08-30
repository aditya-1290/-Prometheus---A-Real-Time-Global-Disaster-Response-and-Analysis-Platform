from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import httpx
from shared.config import Settings, get_settings

app = FastAPI(title="Prometheus Command & Control API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = "your-secret-key"  # Move to environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: EmailStr
    role: str
    organization: str

class EventSummary(BaseModel):
    id: int
    type: str
    severity: str
    location: Dict[str, float]
    status: str
    started_at: datetime
    affected_population: Optional[int]
    confidence_score: float

class ResourceStatus(BaseModel):
    id: int
    type: str
    name: str
    status: str
    location: Dict[str, float]
    capacity: Optional[int]
    last_updated: datetime

# Authentication functions
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return User(**payload)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

# Routes
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # TODO: Implement actual user authentication
    if form_data.username != "demo" or form_data.password != "demo":
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = jwt.encode(
        {
            "username": form_data.username,
            "email": "demo@example.com",
            "role": "admin",
            "organization": "Demo Org",
            "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return Token(access_token=access_token, token_type="bearer")

@app.get("/events/active", response_model=List[EventSummary])
async def get_active_events(user: User = Depends(get_current_user)):
    """Get all active disaster events"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8080/api/correlation/events/active/")
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error fetching events")
        return response.json()

@app.get("/events/{event_id}/impact", response_model=Dict[str, Any])
async def get_event_impact(
    event_id: int,
    user: User = Depends(get_current_user)
):
    """Get impact assessment for a specific event"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8080/api/geo/impact-zones/?event={event_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error fetching impact data")
        return response.json()

@app.get("/resources/nearby", response_model=List[ResourceStatus])
async def get_nearby_resources(
    lat: float,
    lon: float,
    radius: float = 5000,  # meters
    resource_type: Optional[str] = None,
    user: User = Depends(get_current_user)
):
    """Get available resources near a location"""
    async with httpx.AsyncClient() as client:
        params = {
            "lat": lat,
            "lon": lon,
            "radius": radius,
            "type": resource_type
        }
        response = await client.get(
            "http://localhost:8080/api/geo/assets/nearby/",
            params=params
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error fetching resources")
        return response.json()

@app.post("/events/{event_id}/response")
async def coordinate_response(
    event_id: int,
    resources: List[int],
    user: User = Depends(get_current_user)
):
    """Coordinate response for an event by assigning resources"""
    # TODO: Implement resource assignment logic
    return {"status": "response coordinated", "assigned_resources": resources}

@app.get("/analytics/summary")
async def get_analytics_summary(user: User = Depends(get_current_user)):
    """Get summary analytics for all events"""
    async with httpx.AsyncClient() as client:
        # Fetch various analytics
        events = await client.get("http://localhost:8080/api/correlation/events/")
        resources = await client.get("http://localhost:8080/api/geo/assets/")
        impact = await client.get("http://localhost:8080/api/geo/impact-zones/")
        
        if not all(r.status_code == 200 for r in [events, resources, impact]):
            raise HTTPException(status_code=500, detail="Error fetching analytics")
        
        return {
            "total_events": len(events.json()),
            "active_events": len([e for e in events.json() if e["status"] == "active"]),
            "available_resources": len(resources.json()),
            "total_impact_zones": len(impact.json())
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
