from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from db.mongo import get_telemetry_collection, ping_mongodb

app = FastAPI(
    title="Renewable IoT API",
    description="API de lecture des données énergétiques depuis MongoDB",
    version="1.0.0"
)


def serialize_doc(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


@app.get("/")
def root():
    return {
        "message": "API Renewable IoT opérationnelle",
        "endpoints": [
            "/health",
            "/telemetry/latest",
            "/telemetry/history",
            "/telemetry/devices"
        ]
    }


@app.get("/health")
def health():
    try:
        ping_mongodb()
        return {
            "status": "ok",
            "mongodb": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB non accessible: {str(e)}")


@app.get("/telemetry/latest")
def get_latest(device_id: Optional[str] = None):
    collection = get_telemetry_collection()

    query = {}
    if device_id:
        query["device_id"] = device_id

    doc = collection.find_one(query, sort=[("timestamp", -1)])

    if doc is None:
        raise HTTPException(status_code=404, detail="Aucune donnée trouvée")

    return serialize_doc(doc)


@app.get("/telemetry/history")
def get_history(
    device_id: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=500)
):
    collection = get_telemetry_collection()

    query = {}
    if device_id:
        query["device_id"] = device_id

    docs = list(collection.find(query).sort("timestamp", -1).limit(limit))

    return {
        "count": len(docs),
        "items": [serialize_doc(doc) for doc in docs]
    }


@app.get("/telemetry/devices")
def get_devices():
    collection = get_telemetry_collection()
    devices = collection.distinct("device_id")

    return {
        "count": len(devices),
        "devices": sorted(devices)
    }
@app.get("/telemetry/series")
def get_series(device_id: str = "system_01", limit: int = 100):
    collection = get_telemetry_collection()

    projection = {
        "_id": 0,
        "timestamp": 1,
        "simulated_hour": 1,
        "pv_power_kw": 1,
        "load_power_kw": 1,
        "net_power_kw": 1,
        "battery_soc": 1,
        "battery_mode": 1,
    }

    docs = list(
        collection.find({"device_id": device_id}, projection)
        .sort("timestamp", 1)
        .limit(limit)
    )

    return docs
@app.get("/telemetry/latest-state")
def get_latest_state(device_id: str = "system_01"):
    collection = get_telemetry_collection()

    projection = {
        "_id": 0,
        "timestamp": 1,
        "pv_power_kw": 1,
        "load_power_kw": 1,
        "net_power_kw": 1,
        "battery_soc": 1,
        "battery_mode": 1,
    }

    doc = collection.find_one(
        {"device_id": device_id},
        projection,
        sort=[("timestamp", -1)]
    )

    if doc is None:
        raise HTTPException(status_code=404, detail="Aucune donnée trouvée")

    return doc
@app.get("/telemetry/battery-series")
def get_battery_series(limit: int = 100):
    collection = get_telemetry_collection()

    projection = {
        "_id": 0,
        "timestamp": 1,
        "soc": 1,
        "battery_power_kw": 1,
        "mode": 1,
    }

    docs = list(
        collection.find({"device_id": "battery_01"}, projection)
        .sort("timestamp", 1)
        .limit(limit)
    )

    return docs