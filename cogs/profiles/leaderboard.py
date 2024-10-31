from pymongo import DESCENDING
import pandas as pd
import dataframe_image as dfi

from discord import slash_command, Option, ApplicationContext, Color, File
from discord.ext import commands

from utils.data.database import db_players
from utils.maths.ranks import getRankByMMR


class leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="leaderboard", description="Show the leaderboard")
    async def leaderboard(
        self,
        ctx: ApplicationContext,
        sort=Option(
            str,
            name="sort",
            description="Sort the leaderboard, default is MMR",
            required=False,
            choices=["MMR", "Wins", "Losses", "Winrate %"],
            default="MMR",
        ),
        page=Option(
            int,
            name="page",
            description="Page number, default is 1",
            required=False,
            default=1,
        ),
    ):

        page_index = page
        skip_count = 10 * (page_index - 1)  # Number of entries to skip
        placements = [i + skip_count + 1 for i in range(10)]

        data = list(
            db_players.find().sort(sort.lower(), DESCENDING).skip(skip_count).limit(10)
        )

        keys = ["name", "mmr", "wins", "losses"]
        tabledata = {
            "Placement": placements,
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
            tabledata["Rank"].append(getRankByMMR(player["mmr"]).name)
            tabledata["MMR"].append(player["mmr"])
            tabledata["Wins"].append(wins)
            tabledata["Losses"].append(losses)
            winrate = round(wins / (wins + losses) * 100, 2) if wins + losses > 0 else 0
            tabledata["Winrate %"].append(winrate)

        df = pd.DataFrame(tabledata).set_index("Placement")
        # df = df.sort_values(by="MMR", ascending=False)

        # Format the Winrate to display only two decimal places
        df["Winrate %"] = df["Winrate %"].map("{:.2f}".format)

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
            ),
            dpi=200,
            filename="leaderboard-table.png",
        )

        file = File("leaderboard-table.png")
        await ctx.respond(
            content=f"## Leaderboard sorted by {sort} (page {page})", file=file
        )


def setup(bot: commands.Bot):
    bot.add_cog(leaderboard(bot))
