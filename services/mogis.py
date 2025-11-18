from typing import TYPE_CHECKING
from utils.data.data_manager import data_manager

if TYPE_CHECKING:
    from models.MogiModel import MogiHistoryData


async def get_all_mogi_history() -> list["MogiHistoryData"]:
    return await data_manager.Mogis.get_all_mogis()


async def add_bulk_mmr(usernames: list[str], amount: int) -> None:
    return await data_manager.Mogis.bulk_add_mmr(usernames=usernames, amount=amount)
