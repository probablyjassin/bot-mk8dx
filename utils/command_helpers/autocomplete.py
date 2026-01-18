from discord import AutocompleteContext
from rapidfuzz import process, fuzz
import time

from services.players import get_all_player_names
from services.guilds import get_all_guild_names

# Cache for player names
_player_names_cache = None
_guild_names_cache = None
__guilds_cache_timestamp = 0
__players_cache_timestamp = 0
CACHE_DURATION = 60 * 5


async def player_name_autocomplete(ctx: AutocompleteContext) -> list[str]:
    global _player_names_cache, __players_cache_timestamp

    user_input = ctx.value
    current_time = time.time()

    # Update cache if expired or empty
    if (
        _player_names_cache is None
        or (current_time - __players_cache_timestamp) > CACHE_DURATION
    ):
        _player_names_cache = await get_all_player_names()
        __players_cache_timestamp = current_time
        print(f"Player names cache refreshed ({len(_player_names_cache)} players)")

    all_player_names = _player_names_cache

    if not user_input:
        return all_player_names[:10]

    top_matches = process.extract(
        user_input,
        all_player_names,
        limit=5,
        scorer=fuzz.WRatio,
        score_cutoff=60,
    )

    return [match[0] for match in top_matches]


async def guild_name_autocomplete(ctx: AutocompleteContext) -> list[str]:
    global _guild_names_cache, __guilds_cache_timestamp

    user_input = ctx.value
    current_time = time.time()

    # Update cache if expired or empty
    if (
        _guild_names_cache is None
        or (current_time - __guilds_cache_timestamp) > CACHE_DURATION
    ):
        _guild_names_cache = await get_all_guild_names()
        __guilds_cache_timestamp = current_time
        print(f"Guild names cache refreshed ({len(_guild_names_cache)} players)")

    all_guild_names = _guild_names_cache

    if not user_input:
        return all_guild_names[:5]

    top_matches = process.extract(
        user_input,
        all_guild_names,
        limit=5,
        scorer=fuzz.WRatio,
        score_cutoff=60,
    )

    return [match[0] for match in top_matches]
