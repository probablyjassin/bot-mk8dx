from bson.int64 import Int64
from utils.data.database import db_players, db_archived
from models.PlayerModel import PlayerProfile


def search_player(
    search_query: str | Int64 | int, from_archive: bool = False
) -> PlayerProfile | None:
    """
    ## Search for a player in the database.
    Allow searching by both name and discord_id/mention. Performs both searches.
    """
    target_collection = db_players if not from_archive else db_archived

    potential_player = target_collection.find_one(
        {
            "$or": [
                {
                    "name": (
                        search_query.lower()
                        if isinstance(search_query, str)
                        else search_query
                    )
                },
                {
                    "discord_id": (
                        Int64(search_query)
                        if isinstance(search_query, Int64 | int)
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
