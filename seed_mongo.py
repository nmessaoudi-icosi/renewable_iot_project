from datetime import datetime, timedelta, timezone

from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_TELEMETRY

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_TELEMETRY]

base_time = datetime.now(timezone.utc)

sample_docs = []

for i in range(12):
    ts = (base_time - timedelta(minutes=15 * i)).isoformat()

    pv_power = round(1.5 + i * 0.2, 3)
    load_power = round(2.0 + i * 0.1, 3)
    net_power = round(pv_power - load_power, 3)
    soc = round(50 + i * 0.8, 2)

    sample_docs.append({
        "device_id": "pv_01",
        "timestamp": ts,
        "simulated_hour": round(6 + i * 0.25, 2),
        "power_kw": pv_power
    })

    sample_docs.append({
        "device_id": "load_01",
        "timestamp": ts,
        "simulated_hour": round(6 + i * 0.25, 2),
        "power_kw": load_power
    })

    sample_docs.append({
        "device_id": "battery_01",
        "timestamp": ts,
        "simulated_hour": round(6 + i * 0.25, 2),
        "soc": soc,
        "battery_power_kw": abs(net_power),
        "mode": "charging" if net_power > 0 else "discharging"
    })

    sample_docs.append({
        "device_id": "system_01",
        "timestamp": ts,
        "simulated_hour": round(6 + i * 0.25, 2),
        "pv_power_kw": pv_power,
        "load_power_kw": load_power,
        "net_power_kw": net_power,
        "battery_soc": soc,
        "battery_mode": "charging" if net_power > 0 else "discharging"
    })

collection.delete_many({})
result = collection.insert_many(sample_docs)

print(f"{len(result.inserted_ids)} documents insérés dans MongoDB.")
print(f"Base: {MONGO_DB_NAME}")
print(f"Collection: {MONGO_COLLECTION_TELEMETRY}")