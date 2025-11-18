from typing import TYPE_CHECKING
from utils.data.data_manager import data_manager

if TYPE_CHECKING:
    from models.GuildModel import Guild, PlayingGuild


async def apply_guild_mmr(guilds: list["Guild | PlayingGuild"], mmr_deltas: list[int]):
    data_to_update_obj: list[dict[str, str | int]] = [
        {
            "name": guilds[i].name,
            "new_mmr": guilds[i].mmr + mmr_deltas[i],
            "delta": mmr_deltas[i],
        }
        for i in range(len(guilds))
    ]

    await data_manager.Guilds.apply_result_mmr(data_to_update_obj)
