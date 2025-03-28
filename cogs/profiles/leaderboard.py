from io import BytesIO
from pymongo import DESCENDING
import pandas as pd
import dataframe_image as dfi

import discord
from discord import slash_command, Option, File
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from utils.data.database import db_players
from models.RankModel import Rank


class leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="leaderboard", description="Show the leaderboard")
    async def leaderboard(
        self,
        ctx: MogiApplicationContext,
        sort=Option(
            str,
            name="sort",
            description="Sort the leaderboard, default is MMR",
            required=False,
            choices=["MMR", "Wins", "Losses", "Winrate %"],
            default="MMR",
        ),
        page_index=Option(
            int,
            name="page",
            description="Page number, default is 1",
            required=False,
            default=1,
        ),
    ):
        max_players = db_players.count_documents({})

        page_index = page_index if page_index > 0 else 1
        max_pages = -(-max_players // 10)

        page_index = page_index if page_index <= max_pages else max_pages

        skip_count = 10 * (page_index - 1)
        skip_count = skip_count if skip_count < max_players else max_players - 10
        skip_count = skip_count if skip_count >= 0 else 0

        if sort == "MMR":
            data = list(
                db_players.find().sort("mmr", DESCENDING).skip(skip_count).limit(10)
            )
        else:
            data = list(db_players.find())
            for player in data:
                player["Wins"] = len(
                    [delta for delta in player["history"] if delta >= 0]
                )
                player["Losses"] = len(
                    [delta for delta in player["history"] if delta < 0]
                )
                player["Winrate %"] = (
                    round(player["Wins"] / (player["Wins"] + player["Losses"]) * 100, 2)
                    if player["Wins"] + player["Losses"] > 0
                    else 0
                )

            data.sort(key=lambda x: x[sort], reverse=True)
            data = data[skip_count : skip_count + 10]

        tabledata = {
            "Placement": [i + skip_count + 1 for i in range(len(data))],
            "Player": [],
            "Rank": [],
            "MMR": [],
            "Wins": [],
            "Losses": [],
            "Winrate %": [],
        }

        for player in data:
            wins = len([delta for delta in player["history"] if delta > 0])
            losses = len([delta for delta in player["history"] if delta < 0])

            tabledata["Player"].append(player["name"])
            tabledata["Rank"].append(Rank.getRankByMMR(player["mmr"]).rankname)
            tabledata["MMR"].append(player["mmr"])
            tabledata["Wins"].append(wins)
            tabledata["Losses"].append(losses)
            winrate = round(wins / (wins + losses) * 100, 2) if wins + losses > 0 else 0
            tabledata["Winrate %"].append(winrate)

        df = pd.DataFrame(tabledata)
        df = df.sort_values(by=sort, ascending=False)

        df["Placement"] = range(skip_count + 1, skip_count + len(df) + 1)
        df = df.set_index("Placement")

        # Format the Winrate to display only two decimal places
        df["Winrate %"] = df["Winrate %"].map("{:.2f}".format)

        buffer = BytesIO()

        await dfi.export_async(
            df.style.set_table_styles(
                [
                    {
                        "selector": "table",
                        "props": [("border", "none")],
                    },
                    {
                        "selector": "caption",
                        "props": [
                            ("background-color", "rgba(21, 21, 40, 1)"),
                            ("color", "rgba(202, 202, 227, 1)"),
                            ("text-align", "left"),
                            ("font-size", "16px"),
                            ("font-weight", "bold"),
                            ("padding", "7px"),
                        ],
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
                        "props": [
                            ("background-color", "rgba(21, 21, 40, 1)"),
                            ("color", "rgba(202, 202, 227, 1)"),
                        ],
                    },
                    {
                        "selector": "tr:nth-child(odd)",
                        "props": [
                            ("background-color", "rgba(15, 15, 28, 1)"),
                            ("color", "rgba(202, 202, 227, 1)"),
                        ],
                    },
                ]
            ).set_caption(f"Leaderboard sorted by {sort} | Page {page_index}"),
            buffer,
            dpi=200,
            table_conversion="playwright_async",
        )
        buffer.seek(0)

        file = File(buffer, filename="leaderboard-table.png")

        class WebsiteLinkView(discord.ui.View):
            def __init__(self):
                super().__init__(
                    timeout=None
                )  # Timeout set to None to keep the view persistent
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
