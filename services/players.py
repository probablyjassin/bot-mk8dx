from utils.data.data_manager import data_manager
from database.types import archive_type

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.PlayerModel import PlayerProfile


async def get_all_player_profiles(
    archive: archive_type = archive_type.NO,
    with_id: bool = False,
    as_json: bool = False,
) -> list["PlayerProfile"] | list[dict] | None:
    return await data_manager.Players.get_profiles(
        archive=archive, with_id=with_id, as_json=as_json
    )
