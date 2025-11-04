from models import Mogi
from utils.data.data_manager import data_manager


async def apply_mmr(mogi: Mogi) -> None:

    all_player_names = [player.name for player in mogi.players]
    all_player_mmrs = [player.mmr for player in mogi.players]
    all_player_new_mmrs = [
        all_player_mmrs[i] + mogi.mmr_results_by_group[i]
        for i in range(len(mogi.players))
    ]

    # create objects to hand to the database in bulk
    data_to_update_obj: list[dict[str, str | int]] = [
        {
            "name": all_player_names[i],
            "new_mmr": all_player_new_mmrs[i],
            "delta": mogi.mmr_results_by_group[i],
        }
        # don't update subs unless they gained mmr
        for i in range(len(all_player_names))
        if not any(sub.name == all_player_names[i] for sub in mogi.subs)
        or mogi.mmr_results_by_group[i] > 0
    ]

    data_manager.Mogis.apply_result_mmr(
        data_to_update_obj, mogi.format if not mogi.is_mini else 0
    )
