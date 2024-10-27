"""
This module is responsible for connecting to the MongoDB database.
#### Exports:
    db_players: Collection object
    db_archived: Collection object  
"""

import atexit
from pymongo import MongoClient
from config import MONGO_URI, LOUNGE_DB
from main import logger


client = MongoClient(MONGO_URI)
db = client.get_database(LOUNGE_DB)
db_players = db.get_collection("players")
db_archived = db.get_collection("archived")
db_mogis = db.get_collection("mogis")

logger.info(
    f"***\nConnected to MongoDB. Database: {db.name}\n***",
)


def close_client():
    client.close()


atexit.register(close_client)
