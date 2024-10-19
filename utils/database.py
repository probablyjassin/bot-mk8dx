from pymongo import MongoClient
from config import MONGO_URI
import atexit

client = MongoClient(MONGO_URI)
db = client.get_database("lounge")

def close_client():
    client.close()

atexit.register(close_client)