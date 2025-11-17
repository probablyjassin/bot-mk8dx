from pymongo import UpdateOne
from ._mongodb import db_players, db_mogis

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.MogiModel import MogiHistoryData


async def get_all_mogis(
    with_id: bool = False, as_json: bool = False
) -> list["MogiHistoryData"] | list[dict]:

    from models.MogiModel import MogiHistoryData

    data: list[dict] = await db_mogis.find(
        {}, {"_id": 0} if not (with_id or not as_json) else {}
    ).to_list(length=None)

    if as_json:
        return data
    return [MogiHistoryData.from_dict(mogi) for mogi in data]


async def add_mogi_history(
    started_at: int,
    finished_at: int,
    player_ids: list[int],
    format: int,
    subs: int,
    results: list[int],
    disconnections: int,
) -> None:
    await db_mogis.insert_one(
        {
            "started_at": started_at,
            "finished_at": finished_at,
            "player_ids": player_ids,
            "format": format,
            "subs": subs,
            "results": results,
            "disconnections": disconnections,
        }
    )


async def apply_result_mmr(
    data_to_update_obj: list[dict[str, str | int]], format: int
) -> None:
    """
    ### Apply MMR results to players
    Note: Subs need to be removed prior from this list, the function does not check for this.
    """
    await db_players.bulk_write(
        [
            UpdateOne(
                {"name": entry["name"]},
                {
                    "$set": {"mmr": entry["new_mmr"] if entry["new_mmr"] > 0 else 1},
                    "$push": {"history": entry["delta"]},
                    "$inc": {f"formats.{format}": 1},
                },
                upsert=False,
            )
            for entry in data_to_update_obj
        ]
    )


async def bulk_add_mmr(usernames: list[str], amount: int) -> None:
    await db_players.update_many(
        {"name": {"$in": usernames}}, {"$inc": {"mmr": amount}}
    )
