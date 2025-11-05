from utils.data._database import db_aliases

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.PlayerModel import PlayerProfile


def set_player_alias(player: "PlayerProfile", new_alias: str) -> None:
    db_aliases.update_one(
        {"name": player.name}, {"$set": {"alias": new_alias}}, upsert=True
    )


def get_all_aliases() -> dict[str, str]:
    entries = list(db_aliases.find({}))
    return {entry["name"]: entry["alias"] for entry in entries}
