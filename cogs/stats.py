from discord import slash_command, Color
from discord.ext import commands

from utils.data.database import db_mogis
from models.MogiModel import MogiHistoryData
from models.CustomMogiContext import MogiApplicationContext
from utils.command_helpers.info_embed_factory import create_embed
from datetime import datetime
from collections import Counter


class stats(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="stats", description="Show Lounge stats for the current season")
    async def stats(self, ctx: MogiApplicationContext):
        all_mogis = [MogiHistoryData.from_dict(mogi) for mogi in list(db_mogis.find())]

        durations = [
            datetime.fromtimestamp(mogi.finished_at)
            - datetime.fromtimestamp(mogi.started_at)
            for mogi in all_mogis
        ]
        average_duration_minutes = (
            sum([duration.total_seconds() for duration in durations])
            / len(durations)
            / 60
        )

        average_disconnections = sum([mogi.disconnections for mogi in all_mogis]) / len(
            all_mogis
        )
        average_subs = sum([mogi.subs for mogi in all_mogis]) / len(all_mogis)

        all_results_ever = [result for mogi in all_mogis for result in mogi.results]

        player_id_counts = Counter(
            player_id for mogi in all_mogis for player_id in mogi.player_ids
        )
        top_3_players = player_id_counts.most_common(3)

        most_played_str = "\n".join(
            [f"<@{entry[0]}>: {entry[1]}" for entry in top_3_players]
        )

        key_to_format = {
            1: "FFA",
            2: "2v2",
            3: "3v3",
            4: "4v4",
            6: "6v6",
        }

        formats_dict = {}
        for mogi in all_mogis:
            if key_to_format[mogi.format] not in formats_dict:
                formats_dict[key_to_format[mogi.format]] = 1
            else:
                formats_dict[key_to_format[mogi.format]] += 1

        fields = {
            "Total Mogis played": str(len(all_mogis)),
            "Average Duration": f"{average_duration_minutes:.1f} minutes",
            "Most Mogis played": most_played_str,
            "Average DCs per Mogi": f"{average_disconnections:.1f}",
            "Most DCs in a Mogi": f"{max([mogi.disconnections for mogi in all_mogis])}",
            "Average Subs needed per Mogi": f"{average_subs:.1f}",
            "Average Players per Mogi": f"{sum([len(mogi.player_ids) for mogi in all_mogis]) / len(all_mogis):.1f}",
            "Biggest MMR Changes": f"Gain: {max(all_results_ever)}\n Loss: {min(all_results_ever)}",
            "How often do we play which format?": "\n".join(
                [f"{key}: {formats_dict[key]}" for key in formats_dict.keys()]
            ),
        }

        embed = create_embed(
            "Season 3 Mogi Stats",
            "Some interesting stats",
            "https://raw.githubusercontent.com/mk8dx-yuzu/mk8dx-yuzu.github.io/main/public/images/kawaii_icon_by_kevnkkm.png",
            fields,
            {
                "text": ctx.guild.name,
                "icon_url": ctx.guild.icon.url if ctx.guild.icon else None,
            },
            color=Color.dark_magenta(),
        )

        await ctx.respond(embed=embed)

    @slash_command(name="mogis", description="Show all mogis for the current season")
    async def mogis(self, ctx: MogiApplicationContext):
        await ctx.respond(list((db_mogis.find())))


def setup(bot: commands.Bot):
    bot.add_cog(stats(bot))
