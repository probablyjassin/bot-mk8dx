from discord import slash_command, Option, ApplicationContext
from discord.ext import commands

from utils.command_helpers.checks import is_mogi_open
from utils.data.mogi_manager import mogi_manager

from models.CustomMogiContext import MogiApplicationContext
from models.MogiModel import Mogi


class list_mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="l", description="List the players in this mogi")
    @is_mogi_open()
    async def l(
        self,
        ctx: MogiApplicationContext,
        context=Option(
            name="context",
            description="extra context to give the list",
            required=False,
            choices=["tablestring", "mmr"],
        ),
    ):
        if len(ctx.mogi.players) == 0:
            return await ctx.respond("No players in this mogi.")

        list_of_players = ""

        if context == "tablestring":

            if ctx.mogi.format == 1 or ctx.mogi.format == None:
                list_of_players = "\n\n".join(
                    [f"{player.name} +" for player in ctx.mogi.players]
                )
            else:
                for i, team in enumerate(ctx.mogi.teams):
                    list_of_players += f"{ctx.mogi.team_tags[i]}\n"
                    list_of_players += "\n".join(
                        [f"{player.name} +" for player in team]
                    )
                    list_of_players += "\n\n"

        else:

            if ctx.mogi.format == 1 or ctx.mogi.format == None:
                list_of_players = "\n".join(
                    [
                        (
                            f"{i+1}. {player.name}"
                            if context != "mmr"
                            else f"{i+1}. {player.name} ({player.mmr})"
                        )
                        for i, player in enumerate(ctx.mogi.players)
                    ]
                )

            else:
                for i, team in enumerate(ctx.mogi.teams):
                    list_of_players += f"{ctx.mogi.team_tags[i]}\n"
                    list_of_players += "\n".join(
                        [
                            (
                                f"• {player.name}"
                                if context != "mmr"
                                else f"• {player.name} ({player.mmr})"
                            )
                            for player in team
                        ]
                    )
                    list_of_players += "\n\n"

            max_mmr_player, min_mmr_player = max(
                ctx.mogi.players, key=lambda x: x.mmr
            ), min(ctx.mogi.players, key=lambda x: x.mmr)

            list_of_players += (
                f"""\n
                    Average MMR: {round( sum( [player.mmr for player in ctx.mogi.players] ) / len(ctx.mogi.players) )}
                    Highest MMR: {max_mmr_player.name}: {max_mmr_player.mmr}
                    Lowest MMR: {min_mmr_player.name}: {min_mmr_player.mmr}
                """
                if context == "mmr"
                else ""
            )

        await ctx.respond(f"Players in this mogi:\n{list_of_players}")


def setup(bot: commands.Bot):
    bot.add_cog(list_mogi(bot))
