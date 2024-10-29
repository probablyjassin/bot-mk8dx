from bson.int64 import Int64
from utils.data.database import db_players
from models.PlayerModel import PlayerProfile


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
