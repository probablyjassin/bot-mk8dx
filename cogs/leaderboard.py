from discord import slash_command, Option, ApplicationContext, Color, File
from discord.ext import commands
from utils.data.database import players
import pandas as pd
import dataframe_image as dfi
import math
from matplotlib import colors

def calcRank(mmr):
    ranks = [
        {"name": "Wood", "range": (-math.inf, 1)},
        {"name": "Bronze", "range": (2, 1499)},
        {"name": "Silver", "range": (1400, 2999)},
        {"name": "Gold", "range": (3000, 5099)},
        {"name": "Platinum", "range": (5100, 6999)},
        {"name": "Diamond", "range": (7000, 9499)},
        {"name": "Master", "range": (9500, math.inf)},
    ]
    for range_info in ranks:
        start, end = range_info["range"]
        if start <= mmr <= end:
            return range_info["name"]
    return "---"

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
        skip_count = 10 * (page_index - 1) # Number of entries to skip
        placements = [i + skip_count + 1 for i in range(10)]

        data = list(players.find().sort(sort.lower(), pymongo.DESCENDING).skip(skip_count).limit(10))

        tabledata = {
            "Placement": placements,
            "Player": [player["name"] for player in data],
            "Rank": [calcRank(player["mmr"]) for player in data],
            "MMR": [player["mmr"] for player in data],
            "Wins": [player["wins"] for player in data],
            "Losses": [player["losses"] for player in data],
            "Winrate %": [round(player["wins"] / (player["wins"] + player["losses"]) * 100, 2) for player in data]
        }

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
                        "props": [("background-color", "rgba(21, 21, 40, 1)"), ("color", "rgba(202, 202, 227, 1)")],
                    },
                    {
                        "selector": "tr:nth-child(odd)",
                        "props": [("background-color", "rgba(15, 15, 28, 1)"), ("color", "rgba(202, 202, 227, 1)")],
                    },
                ]
            ),
            dpi=200,
            filename="leaderboard-table.png",
        )

        file = File("leaderboard-table.png");
        await ctx.respond(content=f"## Leaderboard sorted by {sort} (page {page})", file=file)



def setup(bot: commands.Bot):
    bot.add_cog(leaderboard(bot))