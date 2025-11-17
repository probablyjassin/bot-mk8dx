from time import time
from bson.int64 import Int64
from pymongo import UpdateOne
from ._mongodb import db_guilds, db_guild_mogis

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from models.GuildModel import Guild


async def find_guild(
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

    results = db_guilds.aggregate(pipeline)
    potential_guild = await results.to_list(length=1)

    return Guild(**potential_guild[0]) if potential_guild else None


async def get_all_guild_names() -> list[str]:
    return [
        player["name"]
        for player in await db_guilds.find({}, {"name": 1, "_id": 0}).to_list(
            length=None
        )
    ]


async def count() -> int:
    return await db_guilds.count_documents({})


async def create_new_guild(
    name: str, first_member_id: int, icon_url: str | None = None
) -> None:
    await db_guilds.insert_one(
        {
            "name": name,
            "icon": icon_url,
            "player_ids": [Int64(first_member_id)],
            "mmr": 3000,
            "history": [],
            "creation_date": round(time()),
        },
    )


async def add_member(guild: "Guild", player_id: int) -> None:
    if await db_guilds.find_one({"player_ids": Int64(player_id)}):
        raise ValueError("Player already in a guild")
    guild.player_ids.append(Int64(player_id))
    await db_guilds.update_one(
        {"_id": guild._id},
        {"$push": {"player_ids": Int64(player_id)}},
    )


async def remove_member(guild: "Guild", player_id: int) -> None:
    if not await db_guilds.find_one({"player_ids": Int64(player_id)}):
        raise ValueError("Player not in a guild")
    guild.player_ids.remove(Int64(player_id))
    await db_guilds.update_one(
        {"_id": guild._id},
        {"$pull": {"player_ids": Int64(player_id)}},
    )


async def set_attribute(guild: "Guild", attribute, value) -> None:
    setattr(guild, f"_{attribute}", value)
    await db_guilds.update_one(
        {"_id": guild._id},
        {"$set" if value else "$unset": {attribute: value if value else ""}},
    )


async def append_history(guild: "Guild", score: int) -> None:
    guild.history.append(score)
    await db_guilds.update_one(
        {"_id": guild._id},
        {"$push": {"history": score}},
    )


async def save_mogi_history(
    guild_names: list[str],
    players: list[list[int]],
    format: int,
    results: list[int],
    started_at: int,
) -> None:
    await db_guild_mogis.insert_one(
        {
            "guilds": guild_names,
            "players": players,
            "format": format,
            "results": results,
            "started_at": started_at,
            "finished_at": round(time()),
        }
    )


async def delete_guild(guild: "Guild"):
    await db_guilds.delete_one({"_id": guild._id})


async def player_has_guild(player_id: int) -> bool:
    result = await db_guilds.find_one({"player_ids": Int64(player_id)})
    return bool(result)


async def get_player_guild(player_id: int) -> Optional["Guild"]:
    from models.GuildModel import Guild

    potential_guild = await db_guilds.find_one({"player_ids": Int64(player_id)})
    return Guild(**potential_guild) if potential_guild else None


async def apply_result_mmr(data_to_update_obj: list[dict[str, str | int]]):
    await db_guilds.bulk_write(
        [
            UpdateOne(
                {"name": entry["name"]},
                {
                    "$set": {"mmr": entry["new_mmr"] if entry["new_mmr"] > 0 else 1},
                    "$push": {"history": entry["delta"]},
                },
                upsert=False,
            )
            for entry in data_to_update_obj
        ]
    )
