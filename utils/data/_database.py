"""
This module is responsible for connecting to the MongoDB database.
#### Exports:
    db_players: Collection object
    db_archived: Collection object
    db_mogis: Collection object
"""

import atexit

from pymongo import MongoClient
from config import MONGO_URI, LOUNGE_DB

from logger import setup_logger

logger = setup_logger(__name__)


client = MongoClient(MONGO_URI)
db = client.get_database(LOUNGE_DB)
db_players = db.get_collection("players")
db_archived = db.get_collection("archived")
db_mogis = db.get_collection("mogis")
db_aliases = db.get_collection("aliases")


logger.info(
    f"***\nConnected to MongoDB. Database: {db.name}\n***",
)


def close_client():
    client.close()


atexit.register(close_client)
