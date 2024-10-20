import atexit
from pymongo import MongoClient
from config import MONGO_URI, LOUNGE_DB
from bson.int64 import Int64

client = MongoClient(MONGO_URI)
db = client.get_database(LOUNGE_DB)
db_players = db.get_collection("players")
db_archived = db.get_collection("archived")

print(f"---\nConnected to MongoDB. Database: {db.name}\n---", )

def close_client():
    client.close()

atexit.register(close_client)