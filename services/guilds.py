from database import guilds
from typing import TYPE_CHECKING, Optional
from bson.int64 import Int64

if TYPE_CHECKING:
    from models.GuildModel import Guild


async def find_guild(query: int | Int64 | str) -> Optional["Guild"]:
    return await guilds.find_guild(query=query)


async def get_all_guild_names() -> list[str]:
    return await guilds.get_all_guild_names()


async def count_guilds() -> int:
    return await guilds.count()


async def create_new_guild(
    name: str, first_member_id: int, icon_url: str | None = None
) -> None:
    return await guilds.create_new_guild(
        name=name, first_member_id=first_member_id, icon_url=icon_url
    )


async def add_member(guild: "Guild", player_id: int) -> None:
    return await guilds.add_member(guild=guild, player_id=player_id)


async def remove_member(guild: "Guild", player_id: int) -> None:
    return await guilds.remove_member(guild=guild, player_id=player_id)


async def delete_guild(guild: "Guild") -> None:
    return await guilds.delete_guild(guild=guild)


async def player_has_guild(player_id: int) -> bool:
    return await guilds.player_has_guild(player_id=player_id)


async def get_player_guild(player_id: int) -> Optional["Guild"]:
    return await guilds.get_player_guild(player_id=player_id)


async def apply_result_mmr(data_to_update_obj: list[dict[str, str | int]]) -> None:
    return await guilds.apply_result_mmr(data_to_update_obj=data_to_update_obj)


async def save_mogi_history(
    guild_names: list[str],
    players: list[list[int]],
    format: int,
    results: list[int],
    started_at: int,
) -> None:
    return await guilds.save_mogi_history(
        guild_names=guild_names,
        players=players,
        format=format,
        results=results,
        started_at=started_at,
    )


# Internal methods for GuildModel
async def set_guild_attribute(guild: "Guild", attribute: str, value) -> None:
    return await guilds.set_attribute(guild, attribute, value)


async def append_guild_history(guild: "Guild", score: int) -> None:
    return await guilds.append_history(guild, score)
