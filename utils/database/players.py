from bson.int64 import Int64
from time import time
from utils.database.types import archive_type
from utils.data._database import db_players

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.PlayerModel import PlayerProfile


def find_player(
    query: int | Int64 | str,
    archive: archive_type = archive_type.NO,
) -> PlayerProfile | None:
    query_criteria = {
        "$and": [
            {
                "$or": [
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

    potential_player = next(
        db_players.aggregate([{"$match": query_criteria}, {"$limit": 1}]),
        None,
    )

    return PlayerProfile(**potential_player) if potential_player else None


def count() -> int:
    return db_players.count_documents({})


def get_profiles(
    archive: archive_type = archive_type.NO,
    with_id: bool = False,
    as_json: bool = False,
) -> list[PlayerProfile] | list[dict] | None:
    data: list[dict] = list(
        db_players.find(archive.value, {"_id": 0} if not with_id else {})
    )
    if as_json:
        return data
    return [PlayerProfile.from_json(player) for player in data]


def create_new_player(username: str, discord_id: int) -> None:
    db_players.insert_one(
        {
            "name": username,
            "discord_id": Int64(discord_id),
            "mmr": 2000,
            "history": [],
            "joined": round(time()),
        },
    )


def set_attribute(player: PlayerProfile, attribute, value) -> None:
    setattr(player, attribute, value)
    db_players.update_one(
        {"_id": player._id},
        {"$set": {attribute: value}},
    )


def append_history(player: PlayerProfile, score: int) -> None:
    player.history.append(score)
    db_players.update_one(
        {"_id": player._id},
        {"$push": {"history": score}},
    )


def count_format_played(player: PlayerProfile, value):
    player._formats[value] += 1
    db_players.update_one(
        {"_id": player._id},
        {"$inc": {f"formats.{value}": 1}},
    )


def delete_player(player: PlayerProfile):
    db_players.delete_one({"_id": player._id})
