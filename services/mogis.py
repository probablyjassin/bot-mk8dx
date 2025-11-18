from typing import TYPE_CHECKING
from utils.data.data_manager import data_manager

if TYPE_CHECKING:
    from models.MogiModel import MogiHistoryData


async def get_all_mogi_history(
    with_id: bool = False, as_json: bool = False
) -> list["MogiHistoryData"] | list[dict]:
    return await data_manager.Mogis.get_all_mogis(with_id=with_id, as_json=as_json)


async def add_bulk_mmr(usernames: list[str], amount: int) -> None:
    return await data_manager.Mogis.bulk_add_mmr(usernames=usernames, amount=amount)
