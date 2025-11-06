from time import time
from bson.int64 import Int64
from utils.data._database import db_guilds

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from models.GuildModel import Guild


def find_guild(
    query: int | Int64 | str,
) -> Optional["Guild"]:

    from models.GuildModel import Guild

    pipeline = []

    if isinstance(query, str):
        # Add a field that extracts capital letters for shorthand matching
        pipeline.append(
            {
                "$addFields": {
                    "shorthand": {
                        "$reduce": {
                            "input": {"$range": [0, {"$strLenCP": "$name"}]},
                            "initialValue": "",
                            "in": {
                                "$concat": [
                                    "$$value",
                                    {
                                        "$cond": [
                                            {
                                                "$regexMatch": {
                                                    "input": {
                                                        "$substrCP": [
                                                            "$name",
                                                            "$$this",
                                                            1,
                                                        ]
                                                    },
                                                    "regex": "[A-Z]",
                                                }
                                            },
                                            {"$substrCP": ["$name", "$$this", 1]},
                                            "",
                                        ]
                                    },
                                ]
                            },
                        }
                    }
                }
            }
        )

    query_criteria = {
        "$or": [
            {"_id": query},
            (
                {
                    "$or": [
                        {"name": {"$regex": f"^{query}$", "$options": "i"}},
                        {"shorthand": {"$regex": f"^{query}$", "$options": "i"}},
                    ]
                }
                if isinstance(query, str)
                else {"name": query}
            ),
            (
                {"player_ids": Int64(query)}
                if isinstance(query, int | Int64)
                else {"player_ids": None}
            ),
        ]
    }

    pipeline.append({"$match": query_criteria})
    pipeline.append({"$limit": 1})
    pipeline.append({"$unset": "shorthand"})

    potential_guild = next(
        db_guilds.aggregate(pipeline),
        None,
    )

    return Guild(**potential_guild) if potential_guild else None


def get_all_guild_names() -> list[str]:
    return [player["name"] for player in db_guilds.find({}, {"name": 1, "_id": 0})]


def count() -> int:
    return db_guilds.count_documents({})


def create_new_guild(
    name: str, first_member_id: int, icon_url: str | None = None
) -> None:
    db_guilds.insert_one(
        {
            "name": name,
            "icon": icon_url,
            "player_ids": [Int64(first_member_id)],
            "mmr": 2000,
            "history": [],
            "creation_date": round(time()),
        },
    )


def add_member(guild: "Guild", player_id: int) -> None:
    if db_guilds.find_one({"player_ids": Int64(player_id)}):
        raise ValueError("Player already in a guild")
    guild.player_ids.append(Int64(player_id))
    db_guilds.update_one(
        {"_id": guild._id},
        {"$push": {"player_ids": Int64(player_id)}},
    )


def set_attribute(guild: "Guild", attribute, value) -> None:
    setattr(guild, attribute, value)
    db_guilds.update_one(
        {"_id": guild._id},
        {"$set" if value else "$unset": {attribute: value if value else ""}},
    )


def append_history(guild: "Guild", score: int) -> None:
    guild.history.append(score)
    db_guilds.update_one(
        {"_id": guild._id},
        {"$push": {"history": score}},
    )


def delete_guild(guild: "Guild"):
    db_guilds.delete_one({"_id": guild._id})


def player_has_guild(player_id: int) -> bool:
    result = db_guilds.find_one({"player_ids": Int64(player_id)})
    return bool(result)


def get_player_guild(player_id: int) -> dict:
    return db_guilds.find_one({"player_ids": Int64(player_id)})
