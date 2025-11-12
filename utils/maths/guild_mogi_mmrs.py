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

    guild_mmrs_for_calculation: list[int] = [
        player.mmr
        for guild_players in playing_players_per_guild
        for player in guild_players
    ]

    results = calculate_mmr(guild_mmrs_for_calculation, guild_placements, team_size)
    results = [round(abs(score) * 0.5) if score > -20 else score for score in results]

    # Weigh results based on guild MMR
    guild_weight: float = 0.5

    average_player_mmrs: list[float] = [
        sum(player.mmr for player in guild_players) / len(guild_players)
        for guild_players in playing_players_per_guild
    ]

    weighted_results = [
        result * (1 - guild_weight)
        + result * guild_weight * (guilds[i].mmr / average_player_mmrs[i])
        for i, result in enumerate(results)
    ]

    # MMR surplus/deficit to inject into the system per guild
    # Positive = add MMR to pool (inflationary), Negative = remove MMR (deflationary), 0 = zero-sum
    mmr_surplus_per_guild: float = (
        2.0  # Add 2 MMR per guild (e.g., 4 guilds = +8 total MMR)
    )

    total_change = sum(weighted_results)

    # Calculate how much to adjust each guild to achieve desired surplus
    # First normalize to zero, then add the desired surplus
    current_surplus_per_guild = total_change / len(weighted_results)
    adjustment_per_guild = current_surplus_per_guild - mmr_surplus_per_guild

    normalized_results = [
        round(result - adjustment_per_guild) for result in weighted_results
    ]

    return normalized_results


"""
async def guild_calc_new_mmr_2(
    guilds: list[Guild],
    playing_players_per_guild: list[list[PlayerProfile]],
    guild_placements: list[int],
):
    player_mmr_weight: float = 0.15

    team_size: int = len(playing_players_per_guild[0])

    average_active_player_mmrs: list[int] = [
        sum(player.mmr for player in guild_players) / len(guild_players)
        for guild_players in playing_players_per_guild
    ]

    guild_mmrs_for_calculation: list[int] = [
        round(
            math.sqrt(team_size)
            * (
                (1 - player_mmr_weight) * guild.mmr
                + player_mmr_weight * average_active_player_mmrs[i]
            )
        )
        for i, guild in enumerate(guilds)
    ]

    results = calculate_mmr(guild_mmrs_for_calculation, guild_placements, 1)
    results = [abs(score) if score > -10 else score for score in results]
    return [round(score * 1.3) for score in results]

"""
