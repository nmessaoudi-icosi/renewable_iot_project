from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_TELEMETRY

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
telemetry_collection = db[MONGO_COLLECTION_TELEMETRY]


def get_telemetry_collection():
    return telemetry_collection


def ping_mongodb():
    client.admin.command("ping")
    return True