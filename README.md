# Prometheus: Real-Time Global Disaster Response and Analysis Platform

## Overview
Prometheus is an intelligent, event-driven platform that ingests and processes heterogeneous data streams to detect, classify, triangulate, and analyze natural disasters in real-time. The platform provides actionable intelligence to first responders, NGOs, and government agencies.

## Architecture
The system is built around a core event bus (Apache Kafka) with 15+ microservices organized into four main groups:

### Group 1: Data Ingestion & Gateway Services (FastAPI)
- Social Media Ingestor
- Satellite Imagery Fetcher
- Sensor Data Aggregator
- News Radio Transcriber

### Group 2: Core AI/ML Processing Services (Flask)
- NLP Crisis Detector
- CV Wildfire Smoke Detector
- CV Flood Water Detector
- CV Damage Assessment
- Audio Distress Analyzer

### Group 3: Data Fusion, Orchestration & Analytics (Django)
- Event Correlation Engine
- Geospatial Service
- Data Lake Manager

### Group 4: API, Delivery & Management (Django & FastAPI)
- Command Control API
- Real-time Notifier
- Config Dashboard

## Setup Instructions

1. Create and activate a Python virtual environment:
```powershell
python -m venv disaster_env
.\disaster_env\Scripts\activate
```

2. Install required packages:
```powershell
pip install fastapi uvicorn python-multipart python-jose[cryptography] passlib[bcrypt] sqlalchemy psycopg2-binary pydantic websockets httpx python-dotenv kafka-python aiokafka aiohttp pillow opencv-python-headless numpy pydantic-settings aiofiles flask transformers torch tensorflow spacy nltk scikit-learn pandas segmentation-models-pytorch librosa
```

3. Set up Kafka:
- Install and start Apache Kafka
- Create required topics:
  - raw_social_media_messages
  - raw_satellite_images
  - raw_sensor_readings
  - news_transcripts
  - crisis_detections
  - wildfire_detections
  - flood_detections
  - damage_assessments
  - distress_analyses

4. Start the services:

Group 1 (FastAPI Services):
```powershell
# Start Social Media Ingestor
cd services/social_media_ingestor
uvicorn main:app --reload --port 8000

# Start Satellite Imagery Fetcher
cd services/satellite_imagery_fetcher
uvicorn main:app --reload --port 8001

# Start Sensor Data Aggregator
cd services/sensor_data_aggregator
uvicorn main:app --reload --port 8002

# Start News Radio Transcriber
cd services/news_radio_transcriber
uvicorn main:app --reload --port 8003
```

Group 2 (Flask Services):
```powershell
# Start NLP Crisis Detector
cd services/nlp_crisis_detector
python app.py

# Start CV Wildfire Smoke Detector
cd services/cv_wildfire_smoke_detector
python app.py

# Start CV Flood Water Detector
cd services/cv_flood_water_detector
python app.py

# Start CV Damage Assessment
cd services/cv_damage_assessment
python app.py

# Start Audio Distress Analyzer
cd services/audio_distress_analyzer
python app.py
```

## API Documentation
Each service provides its own API documentation:

Group 1 (Swagger UI):
- Social Media Ingestor: http://localhost:8000/docs
- Satellite Imagery Fetcher: http://localhost:8001/docs
- Sensor Data Aggregator: http://localhost:8002/docs
- News Radio Transcriber: http://localhost:8003/docs

Group 2 (Flask APIs):
- NLP Crisis Detector: http://localhost:5000/api/analyze
- CV Wildfire Smoke Detector: http://localhost:5001/api/detect
- CV Flood Water Detector: http://localhost:5002/api/detect
- CV Damage Assessment: http://localhost:5003/api/assess
- Audio Distress Analyzer: http://localhost:5004/api/analyze

## Project Structure
```
.
├── services/
│   ├── social_media_ingestor/
│   ├── satellite_imagery_fetcher/
│   ├── sensor_data_aggregator/
│   ├── news_radio_transcriber/
│   ├── nlp_crisis_detector/
│   ├── cv_wildfire_smoke_detector/
│   ├── cv_flood_water_detector/
│   ├── cv_damage_assessment/
│   ├── audio_distress_analyzer/
│   ├── command_control_api/
│   ├── real_time_notifier/
│   └── config_dashboard/
├── analytics/
│   ├── event_correlation_engine/
│   ├── geospatial_service/
│   └── data_lake_manager/
├── frontend/
│   ├── responder_dashboard/      # React.js Emergency Responder Interface
│   └── public_portal/           # Next.js Public Information Portal
├── shared/
│   ├── event_producer.py
│   ├── config.py
│   └── ml_utils.py
└── infrastructure/
    ├── docker/
    ├── kubernetes/
    └── monitoring/
```

## Running the Complete Platform

### 1. Infrastructure Setup
```bash
# Start infrastructure services
docker-compose up -d kafka redis postgres elasticsearch kibana

# Initialize database
python manage.py migrate
```

### 2. Start Backend Services

Group 1 - Data Ingestion (FastAPI):
```bash
uvicorn services.social_media_ingestor.main:app --port 8000 --reload
uvicorn services.satellite_imagery_fetcher.main:app --port 8001 --reload
uvicorn services.sensor_data_aggregator.main:app --port 8002 --reload
uvicorn services.news_radio_transcriber.main:app --port 8003 --reload
```

Group 2 - AI/ML Processing (Flask):
```bash
python services/nlp_crisis_detector/app.py
python services/cv_wildfire_smoke_detector/app.py
python services/cv_flood_water_detector/app.py
python services/cv_damage_assessment/app.py
python services/audio_distress_analyzer/app.py
```

Group 3 - Analytics (Django):
```bash
python analytics/event_correlation_engine/manage.py runserver 8010
python analytics/geospatial_service/manage.py runserver 8011
python analytics/data_lake_manager/manage.py runserver 8012
```

Group 4 - API & Management:
```bash
python services/command_control_api/manage.py runserver 8020
uvicorn services.real_time_notifier.main:app --port 9001 --reload
python services/config_dashboard/manage.py runserver 8022
```

### 3. Start Frontend Applications

Emergency Responder Dashboard:
```bash
cd frontend/responder_dashboard
npm install
npm run dev  # Runs on http://localhost:3000
```

Public Information Portal:
```bash
cd frontend/public_portal
npm install
npm run dev  # Runs on http://localhost:3001
```

## Environment Variables
Create a `.env` file in the root directory with:
```
# Infrastructure
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
REDIS_URL=redis://localhost:6379
POSTGRES_DB=prometheus
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure_password
POSTGRES_HOST=localhost

# AWS Credentials
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=your_region
S3_BUCKET=your_bucket

# API Keys
TWITTER_API_KEY=your_key
SENTINEL_HUB_KEY=your_key
USGS_API_KEY=your_key

# Service Ports
GROUP1_PORTS=8000-8003
GROUP2_PORTS=5000-5004
GROUP3_PORTS=8010-8012
GROUP4_PORTS=8020,9001,8022
FRONTEND_PORTS=3000,3001

# Security
JWT_SECRET_KEY=your_secret_key
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

## Accessing Services

### APIs and Dashboards
- Emergency Responder Dashboard: http://localhost:3000
- Public Information Portal: http://localhost:3001
- Command Control API: http://localhost:8020/api/v1
- Config Dashboard: http://localhost:8022/admin
- Real-time Notifications WebSocket: ws://localhost:9001/ws

### Documentation
- API Documentation: http://localhost:8020/docs
- Metrics Dashboard: http://localhost:3000/grafana
- Log Analytics: http://localhost:5601 (Kibana)

## Monitoring and Maintenance

### Health Checks
```bash
# Check all services
./scripts/health_check.sh

# Monitor Kafka
./scripts/kafka_monitor.sh
```

### Logs
```bash
# View service logs
docker-compose logs -f service_name

# View ELK logs
http://localhost:5601
```

### Metrics
```bash
# Prometheus metrics
http://localhost:9090

# Grafana dashboards
http://localhost:3000/grafana
```

 Note: I have removed all the environment variables from this application if any developer intends to use please use your env variables.