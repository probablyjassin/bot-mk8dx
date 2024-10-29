from io import BytesIO

import pandas as pd
import dataframe_image as dfi
from matplotlib import colors

from models.MogiModel import Mogi


def create_table(mogi: Mogi) -> BytesIO:

    all_player_names = [player.name for player in mogi.players]
    all_player_mmrs = [player.mmr for player in mogi.players]

    all_player_new_mmrs = [
        all_player_mmrs[i] + mogi.mmr_results_by_group[i]
        for i in range(len(mogi.players))
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
                "selector": "table",
                "props": [("border", "none")],
            },
            {
                "selector": "th",
                "props": [("border", "1px solid rgba(14, 14, 27, 1)")],
            },
            {
                "selector": "td",
                "props": [("border", "1px solid rgba(14, 14, 27, 1)")],
            },
            {
                "selector": "tr:nth-child(even)",
                "props": [("background-color", "rgba(21, 21, 40, 1)"), ("color", "rgba(202, 202, 227, 1)")],
            },
            {
                "selector": "tr:nth-child(odd)",
                "props": [("background-color", "rgba(15, 15, 28, 1)"), ("color", "rgba(202, 202, 227, 1)")],
            },
        ]
    ).background_gradient(
        cmap=colors.LinearSegmentedColormap.from_list(
            "",
            [
                "#E22012",
                "#E22012",
                "#E22012",
                "#CACAE3",
                "#22AA3B",
                "#22AA3B",
                "#22AA3B",
            ],
            ),
            vmin=-150,
            vmax=150,
            subset=["Change"],
        ),
        buffer,
    )

    buffer.seek(0)
    return buffer


# TODO: change the colors
