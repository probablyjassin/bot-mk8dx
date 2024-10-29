"""
This module is responsible for connecting to the MongoDB database.
#### Exports:
    db_players: Collection object
    db_archived: Collection object  
"""

import atexit
from main import logger

from pymongo import MongoClient
from config import MONGO_URI, LOUNGE_DB

from bson.int64 import Int64
from models.PlayerModel import PlayerProfile


client = MongoClient(MONGO_URI)
db = client.get_database(LOUNGE_DB)
db_players = db.get_collection("players")
db_archived = db.get_collection("archived")
db_mogis = db.get_collection("mogis")


def search_player(search_query: str | Int64) -> PlayerProfile | None:
    """
    Allow searching by both name and discord_id/mention. Performs both searches.
    """

    potential_player = db_players.find_one(
        {
            "$or": [
                {"name": search_query},
                {
                    "discord_id": (
                        search_query
                        if isinstance(search_query, Int64)
                        else (
                            Int64(search_query.strip("<@!>"))
                            if search_query.strip("<@!>").isdigit()
                            else None
                        )
                    )
                },
            ]
        }
    )
    return PlayerProfile(**potential_player) if potential_player else None


logger.info(
    f"***\nConnected to MongoDB. Database: {db.name}\n***",
)


def close_client():
    client.close()


atexit.register(close_client)
