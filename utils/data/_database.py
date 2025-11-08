"""
This module is responsible for connecting to the MongoDB database.
"""

import atexit
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

from config import MONGO_URI, LOUNGE_DB

from logger import setup_logger

logger = setup_logger(__name__)


client = AsyncIOMotorClient(MONGO_URI, server_api=ServerApi("1"))
db = client.get_database(LOUNGE_DB)
db_players = db.get_collection("players")
db_guilds = db.get_collection("guilds")
db_mogis = db.get_collection("mogis")
db_aliases = db.get_collection("aliases")


logger.info(
    f"***\nConnected to MongoDB. Database: {db.name}\n***",
)


def close_client():
    client.close()


atexit.register(close_client)
