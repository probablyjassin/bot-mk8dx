from database._mongodb import db_aliases

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.PlayerModel import PlayerProfile


async def set_player_alias(player: "PlayerProfile", new_alias: str) -> None:
    await db_aliases.update_one(
        {"name": player.name}, {"$set": {"alias": new_alias}}, upsert=True
    )


async def get_all_aliases() -> dict[str, str]:
    entries = await db_aliases.find({}).to_list(length=None)
    return {entry["name"]: entry["alias"] for entry in entries}
