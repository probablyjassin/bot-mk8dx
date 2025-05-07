from bson.int64 import Int64

from discord import Guild, Member
from utils.data.database import db_players, db_archived
from models.PlayerModel import PlayerProfile


def search_player(
    search_query: str | Int64 | int,
    with_archive: bool = False,
    archive_only: bool = False,
) -> PlayerProfile | None:
    """
    ## Search for a player in the database.
    Allow searching by both name and discord_id/mention. Performs both searches.
    """
    target_collection = db_players if not archive_only else db_archived

    query_criteria = {
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

    pipeline = [{"$match": query_criteria}, {"$limit": 1}]
    if not archive_only and with_archive:
        pipeline.append({"$unionWith": {"coll": "archive"}})

    potential_player = next(target_collection.aggregate(pipeline), None)

    return PlayerProfile(**potential_player) if potential_player else None


async def get_guild_member(guild: Guild, id: int) -> Member | None:
    member: Member | None = None
    try:
        member = await guild.fetch_member(id)
    except:
        pass
    return member
