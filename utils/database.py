import atexit
from pymongo import MongoClient
from config import MONGO_URI, LOUNGE_DB

client = MongoClient(MONGO_URI)
db = client.get_database(LOUNGE_DB)
players_collection = db.get_collection("players")
archived_collection = db.get_collection("archived")

def close_client():
    client.close()

atexit.register(close_client)