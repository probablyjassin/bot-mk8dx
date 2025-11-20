from io import BytesIO

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import pandas as pd


def create_table(
    names: list[str],
    old_mmrs: list[int],
    results: list[int],
    placements: list[int],
    team_size: int,
) -> BytesIO:

    new_mmrs = [
        max(
            (1, old_mmrs[i] + results[i]),
        )
        for i in range(len(names))
    ]

    data = {
        "Pos.": placements,
        "Player": names,
        "MMR": old_mmrs,
        "Change": [round(results[i]) for i in range(0, len(results))],
        "New MMR": new_mmrs,
    }

    df = pd.DataFrame(data).set_index("Player")
    df = df.sort_values(by="Change", ascending=False)

    if team_size == 1:
        df = df.sort_values(by="Pos.", ascending=True)

    # Calculate appropriate figure size based on table dimensions
    num_rows = len(df) + 1  # +1 for header
    num_cols = len(df.columns) + 1  # +1 for index

    fig_width = num_cols * 1.5
    fig_height = num_rows * 0.8

    # Create figure with calculated size
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis("off")

    # Define colors
    bg_dark = "#0F0F1C"
    bg_light = "#151528"
    text_color = "#CACAE3"
    border_color = "#0E0E1B"

    # Create color mapping for "Change" column
    cmap = mcolors.LinearSegmentedColormap.from_list(
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
    )
    norm = mcolors.Normalize(vmin=-150, vmax=150)

    # Prepare cell colors
    cell_colors = []
    for idx, row in df.iterrows():
        row_colors = []
        for col_idx, col in enumerate(df.columns):
            if col == "Change":
                # Apply gradient color for Change column
                color = cmap(norm(row[col]))
            else:
                # Alternating row colors for other columns
                color = bg_light if df.index.get_loc(idx) % 2 == 0 else bg_dark
            row_colors.append(color)
        cell_colors.append(row_colors)

    # Create table that fills the entire figure
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        rowLabels=df.index,
        cellLoc="center",
        loc="center",
        cellColours=cell_colors,
        colColours=[bg_dark] * len(df.columns),
        rowColours=[bg_light if i % 2 == 0 else bg_dark for i in range(len(df))],
        bbox=[0, 0, 1, 1],  # Make table fill entire axes
    )

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(16)

    # Auto-size columns based on content
    table.auto_set_column_width(col=list(range(len(df.columns))))

    # Set text color and borders
    change_col_idx = df.columns.get_loc("Change") if "Change" in df.columns else None
    for (row, col), cell in table.get_celld().items():
        is_header = row == 0
        is_change_body_cell = (
            change_col_idx is not None and not is_header and col == change_col_idx
        )

        # Use black text for the colored "Change" column body cells; keep others light
        cell_text_color = "#000000" if is_change_body_cell else text_color

        cell.set_text_props(
            color=cell_text_color, weight="bold" if is_header else "normal"
        )
        cell.set_edgecolor(border_color)
        cell.set_linewidth(1.5)
        cell.set_height(1.0 / num_rows)

    # Set background color
    fig.patch.set_facecolor(bg_dark)

    # Save to buffer with no extra padding
    buffer = BytesIO()
    plt.savefig(
        buffer,
        format="png",
        facecolor=bg_dark,
        bbox_inches="tight",
        pad_inches=0.1,
        dpi=200,
    )
    plt.close()

    buffer.seek(0)
    return buffer
