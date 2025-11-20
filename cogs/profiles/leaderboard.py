from io import BytesIO
import asyncio

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd

import discord
from discord import slash_command, Option, File
from discord.ext import commands

from models import MogiApplicationContext, Rank
from utils.data import data_manager
from utils.database.types import sort_type


class leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="leaderboard", description="Show the leaderboard")
    async def leaderboard(
        self,
        ctx: MogiApplicationContext,
        sort: str = Option(
            name="sort",
            description="Sort the leaderboard, default is MMR",
            required=False,
            default="MMR",
            choices=["MMR", "Wins", "Losses", "Winrate %"],
        ),
        page_index=Option(
            int,
            name="page",
            description="Page number, default is 1",
            required=False,
            default=1,
        ),
    ):
        await ctx.defer()

        total_player_count = await data_manager.Players.count()

        page_index = page_index if page_index > 0 else 1
        max_pages = -(-total_player_count // 10)

        page_index = page_index if page_index <= max_pages else max_pages

        skip_count = 10 * (page_index - 1)
        skip_count = (
            skip_count if skip_count < total_player_count else total_player_count - 10
        )
        skip_count = skip_count if skip_count >= 0 else 0

        data = await data_manager.Leaderboard.get_leaderboard(
            page_index=page_index, sort=sort_type[sort]
        )

        def create_table():
            tabledata: dict[str, list] = {
                "Placement": [i + skip_count + 1 for i in range(len(data))],
                "Player": [],
                "Rank": [],
                "MMR": [],
                "Wins": [],
                "Losses": [],
                "Winrate %": [],
            }

            for player in data:
                tabledata["Player"].append(player["name"])
                tabledata["Rank"].append(Rank.getRankByMMR(player["mmr"]).rankname)
                tabledata["MMR"].append(player["mmr"])
                tabledata["Wins"].append(player["Wins"])
                tabledata["Losses"].append(player["Losses"])
                tabledata["Winrate %"].append(f"{round(player['Winrate %'], 2):.2f}")

            df = pd.DataFrame(tabledata)
            df["Placement"] = range(skip_count + 1, skip_count + len(df) + 1)
            df = df.set_index("Placement")

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

            # Prepare cell colors - alternating rows
            cell_colors = []
            for idx, row in df.iterrows():
                row_colors = []
                for col in df.columns:
                    # Alternating row colors
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
                rowColours=[
                    bg_light if i % 2 == 0 else bg_dark for i in range(len(df))
                ],
                bbox=[0, 0, 1, 1],  # Make table fill entire axes
            )

            # Style the table
            table.auto_set_font_size(False)
            table.set_fontsize(16)

            # Auto-size columns based on content
            table.auto_set_column_width(col=list(range(len(df.columns))))

            # Set text color and borders
            for (row, col), cell in table.get_celld().items():
                is_header = row == 0

                cell.set_text_props(
                    color=text_color, weight="bold" if is_header else "normal"
                )
                cell.set_edgecolor(border_color)
                cell.set_linewidth(1.5)
                cell.set_height(1.0 / num_rows)

            # Set background color
            fig.patch.set_facecolor(bg_dark)

            # Add title as text above the table
            fig.text(
                0.5,
                0.98,
                f"Leaderboard sorted by {sort} | Page {page_index}",
                ha="center",
                va="top",
                fontsize=18,
                weight="bold",
                color=text_color,
            )

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

        # Run the table creation in a thread to avoid blocking
        buffer = await asyncio.to_thread(create_table)

        file = File(buffer, filename="leaderboard-table.png")

        class WebsiteLinkView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(
                    discord.ui.Button(
                        label="View on Website",
                        style=discord.ButtonStyle.link,
                        url=f"https://mk8dx-yuzu.github.io/",
                    )
                )

        await ctx.respond(file=file, view=WebsiteLinkView())


def setup(bot: commands.Bot):
    bot.add_cog(leaderboard(bot))
