from bson.int64 import Int64
from time import time
from utils.database.types import archive_type
from utils.data._database import db_players

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from models.PlayerModel import PlayerProfile


async def find_player(
    query: int | Int64 | str,
    archive: archive_type = archive_type.NO,
) -> Optional["PlayerProfile"]:

    from models.PlayerModel import PlayerProfile

    query_criteria = {
        "$and": [
            {
                "$or": [
                    {"_id": query},
                    {"name": (query.lower() if isinstance(query, str) else query)},
                    {
                        "discord_id": (
                            Int64(query)
                            if isinstance(query, Int64 | int)
                            else (
                                Int64(query.strip("<@!>"))
                                if query.strip("<@!>").isdigit()
                                else None
                            )
                        )
                    },
                ]
            },
            archive.value,
        ]
    }

    results = await db_players.aggregate(
        [{"$match": query_criteria}, {"$limit": 1}]
    ).to_list(length=1)
    potential_player = results[0] if results else None

    return PlayerProfile(**potential_player) if potential_player else None


async def count() -> int:
    return await db_players.count_documents({})


async def get_profiles(
    archive: archive_type = archive_type.NO,
    with_id: bool = False,
    as_json: bool = False,
) -> list["PlayerProfile"] | list[dict] | None:

    from models.PlayerModel import PlayerProfile

    data: list[dict] = await db_players.find(
        archive.value, {"_id": 0} if not with_id else {}
    ).to_list(length=None)

    if as_json:
        return data
    return [PlayerProfile.from_json(player) for player in data]


async def get_all_player_names() -> list[str]:
    cursor = db_players.find({}, {"name": 1, "_id": 0})
    return await cursor.to_list(length=None)


async def create_new_player(username: str, discord_id: int) -> None:
    await db_players.insert_one(
        {
            "name": username,
            "discord_id": Int64(discord_id),
            "mmr": 2000,
            "history": [],
            "formats": {str(i): 0 for i in range(7)},
            "joined": round(time()),
        },
    )


async def set_attribute(player: "PlayerProfile", attribute, value) -> None:
    setattr(player, f"_{attribute}", value)
    await db_players.update_one(
        {"_id": player._id},
        {"$set" if value else "$unset": {attribute: value if value else ""}},
    )


async def append_history(player: "PlayerProfile", score: int) -> None:
    player.history.append(score)
    await db_players.update_one(
        {"_id": player._id},
        {"$push": {"history": score}},
    )


async def count_format_played(player: "PlayerProfile", value):
    player._formats[value] += 1
    await db_players.update_one(
        {"_id": player._id},
        {"$inc": {f"formats.{value}": 1}},
    )


async def delete_player(player: "PlayerProfile"):
    await db_players.delete_one({"_id": player._id})
