from database import aliases, leaderboard
from database.types import archive_type, sort_type
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.PlayerModel import PlayerProfile


# Aliases
async def set_player_alias(player: "PlayerProfile", new_alias: str) -> None:
    return await aliases.set_player_alias(player=player, new_alias=new_alias)


async def get_all_aliases() -> dict[str, str]:
    return await aliases.get_all_aliases()


# Leaderboard
async def get_leaderboard(
    page_index: int,
    sort: sort_type = sort_type.MMR,
    archive: archive_type = archive_type.NO,
) -> list[dict] | None:
    return await leaderboard.get_leaderboard(
        page_index=page_index, sort=sort, archive=archive
    )
