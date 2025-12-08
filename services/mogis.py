from typing import TYPE_CHECKING, Optional, Union
from database import mogis

if TYPE_CHECKING:
    from models.MogiModel import MogiHistoryData


async def get_latest_mogi(
    as_json: bool = False,
) -> Optional[Union["MogiHistoryData", dict]]:
    return await mogis.get_latest_mogi(as_json=as_json)


async def update_latest_mogi(new_results: list[int]) -> None:
    await mogis.update_latest_mogi(new_results=new_results)


async def get_all_mogi_history(
    with_id: bool = False, as_json: bool = False
) -> list["MogiHistoryData"] | list[dict]:
    return await mogis.get_all_mogis(with_id=with_id, as_json=as_json)


async def add_bulk_mmr(usernames: list[str], amount: int) -> None:
    return await mogis.bulk_add_mmr(usernames=usernames, amount=amount)


async def add_mogi_history(
    started_at: int,
    finished_at: int,
    player_ids: list[int],
    format: int,
    subs: int,
    results: list[int],
    disconnections: int,
) -> None:
    return await mogis.add_mogi_history(
        started_at=started_at,
        finished_at=finished_at,
        player_ids=player_ids,
        format=format,
        subs=subs,
        results=results,
        disconnections=disconnections,
    )


async def apply_result_mmr(
    data_to_update_obj: list[dict[str, str | int]], format: int
) -> None:
    return await mogis.apply_result_mmr(
        data_to_update_obj=data_to_update_obj, format=format
    )
