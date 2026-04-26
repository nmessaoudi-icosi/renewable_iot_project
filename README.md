# Renewable IoT Project

Simulation d’un système énergétique (PV, Load, Battery) avec :
- MQTT (Mosquitto)
- MongoDB
- FastAPI

## Lancer le projet

### 1. MongoDB
python seed_mongo.py

### 2. MQTT
Mosquitto doit être actif

### 3. Simulation
python main.py

### 4. API
uvicorn api_server:app --reload
