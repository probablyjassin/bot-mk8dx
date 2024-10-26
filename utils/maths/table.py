from io import BytesIO

import pandas as pd
import dataframe_image as dfi
from matplotlib import colors

from models.MogiModel import Mogi


def create_table(mogi: Mogi) -> BytesIO:

    all_player_names = [player.name for team in mogi.teams for player in team]
    all_player_mmrs = [player.mmr for team in mogi.teams for player in team]

    all_player_new_mmrs = [
        all_player_mmrs[i] + mogi.mmr_results_by_group[i]
        for i in range(0, len(mogi.players))
    ]

    data = {
        "Pos.": mogi.placements_by_group,
        "Player": all_player_names,
        "MMR": all_player_mmrs,
        "Change": [
            round(mogi.mmr_results_by_group[i]) for i in range(0, len(mogi.players))
        ],
        "New MMR": all_player_new_mmrs,
    }

    df = pd.DataFrame(data).set_index("Player")
    df = df.sort_values(by="Change", ascending=False)

    if mogi.format == 1:
        df = df.sort_values(by="Pos.", ascending=True)

    buffer = BytesIO()
    dfi.export(
        df.style.set_table_styles(
            [
                {
                    "selector": "tr:nth-child(even)",
                    "props": [("background-color", "#363f4f"), ("color", "white")],
                },
                {
                    "selector": "tr:nth-child(odd)",
                    "props": [("background-color", "#1d2735"), ("color", "white")],
                },
            ]
        ).background_gradient(
            cmap=colors.LinearSegmentedColormap.from_list(
                "", ["red", "red", "white", "green", "green"]
            ),
            low=0.3,
            high=0.2,
            subset=["Change"],
        ),
        buffer,
    )

    buffer.seek(0)
    return buffer
