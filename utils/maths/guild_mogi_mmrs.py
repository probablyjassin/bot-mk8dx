import math
from models.GuildModel import Guild
from models.PlayerModel import PlayerProfile
from .mmr_algorithm import calculate_mmr


async def guild_calc_new_mmr(
    guilds: list[Guild],
    playing_players_per_guild: list[list[PlayerProfile]],
    guild_placements: list[int],
):
    team_size: int = len(playing_players_per_guild[0])

    average_active_player_mmrs: list[int] = [
        sum(player.mmr for player in guild_players) / len(guild_players)
        for guild_players in playing_players_per_guild
    ]

    guild_mmrs_for_calculation: list[int] = [
        round(math.sqrt(team_size) * (guild.mmr + average_active_player_mmrs[i]))
        for i, guild in enumerate(guilds)
    ]

    return calculate_mmr(guild_mmrs_for_calculation, guild_placements, 1)
