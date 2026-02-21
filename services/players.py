from database import players
from database.types import archive_type

from typing import TYPE_CHECKING, Optional
from bson.int64 import Int64

if TYPE_CHECKING:
    from models.PlayerModel import PlayerProfile


async def get_all_player_profiles(
    archive: archive_type = archive_type.NO,
    with_id: bool = False,
    as_json: bool = False,
) -> list["PlayerProfile"] | list[dict] | None:
    return await players.get_profiles(archive=archive, with_id=with_id, as_json=as_json)


async def find_player_profile(
    query: int | Int64 | str, archive: archive_type = archive_type.NO
) -> Optional["PlayerProfile"]:
    return await players.find_player(query=query, archive=archive)


async def find_player_profiles_by_ids(
    player_ids: list[int | Int64],
) -> list["PlayerProfile"]:
    return await players.find_list(player_ids=player_ids)


async def create_new_player(username: str, discord_id: int, flag: str) -> None:
    return await players.create_new_player(
        username=username, discord_id=discord_id, flag=flag
    )


async def get_all_player_names() -> list[str]:
    return await players.get_all_player_names()


async def count_players() -> int:
    return await players.count()


async def delete_player(player: "PlayerProfile") -> None:
    return await players.delete_player(player=player)


# Internal methods for PlayerModel
async def set_player_attribute(player: "PlayerProfile", attribute: str, value) -> None:
    return await players.set_attribute(player=player, attribute=attribute, value=value)


async def append_player_history(player: "PlayerProfile", score: int) -> None:
    return await players.append_history(player=player, score=score)


async def count_player_format_played(player: "PlayerProfile", value) -> None:
    return await players.count_format_played(player=player, value=value)
