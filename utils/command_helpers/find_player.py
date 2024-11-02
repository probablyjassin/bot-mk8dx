from bson.int64 import Int64
from utils.data.database import db_players, db_archived
from models.PlayerModel import PlayerProfile


def search_player(
    search_query: str | Int64, from_archive: bool = False
) -> PlayerProfile | None:
    """
    Allow searching by both name and discord_id/mention. Performs both searches.
    """
    target_collection = db_players if not from_archive else db_archived

    potential_player = target_collection.find_one(
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
