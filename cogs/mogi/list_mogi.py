from typing import Optional

from discord import slash_command, Option, AllowedMentions
from discord.ext import commands

from utils.decorators import is_mogi_open
from models import MogiApplicationContext


class list_mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="l", description="List the players in this mogi")
    @is_mogi_open()
    async def l(
        self,
        ctx: MogiApplicationContext,
        context: Optional[str] = Option(
            str,
            name="context",
            description="extra context to give the list",
            choices=["tablestring", "usernames", "mmr"],
            required=False,
        ),
    ):
        if len(ctx.mogi.players) == 0:
            return await ctx.respond("No players in this mogi.")

        list_of_players = f"Players in this mogi:\n"

        # Tablestring
        if context == "tablestring":
            list_of_players = "```\n"

            # FFA
            if ctx.mogi.format == 1 or ctx.mogi.format == None:
                list_of_players += "-\n" + "\n\n".join(
                    [f"{player.name} +" for player in ctx.mogi.players]
                )

            # Teams
            else:
                for i, team in enumerate(ctx.mogi.teams):
                    list_of_players += f"{ctx.mogi.team_tags[i]}\n"
                    list_of_players += "\n".join(
                        [f"{player.name} +" for player in team]
                    )
                    list_of_players += "\n\n"

            list_of_players += "\n```"

        # Usernames
        elif context == "usernames":

            # FFA
            if ctx.mogi.format == 1 or ctx.mogi.format == None:
                list_of_players += "\n".join(
                    [
                        (f"`{i+1}.` <@{player.discord_id}>")
                        for i, player in enumerate(ctx.mogi.players)
                    ]
                )

            # Teams
            else:
                for i, team in enumerate(ctx.mogi.teams):
                    list_of_players += f"{ctx.mogi.team_tags[i]}\n"
                    list_of_players += "\n".join(
                        [(f"• <@{player.discord_id}>") for player in team]
                    )
                    list_of_players += "\n\n"

        # Normal and MMR
        else:
            # create new independant arrays to sort them
            # (original player and teams arrays may never be tampered with)
            players = ctx.mogi.players[:]

            # MMR: Sort players as well (only in FFA)
            if context == "mmr" and ctx.mogi.format in [None, 1]:
                players.sort(key=lambda x: x.mmr, reverse=True)

            # FFA
            if ctx.mogi.format in [None, 1]:
                list_of_players += "\n".join(
                    [
                        (
                            f"`{i+1}.` {player.name}"
                            if context != "mmr"
                            else f"`{i+1}.` {player.name} ({player.mmr})"
                        )
                        for i, player in enumerate(players)
                    ]
                )

            # Teams
            else:
                for i, team in enumerate(ctx.mogi.teams):
                    list_of_players += f"### {ctx.mogi.team_tags[i]}\n"
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

            # MMR info at the end
            max_mmr_player, min_mmr_player = max(players, key=lambda x: x.mmr), min(
                players, key=lambda x: x.mmr
            )

            list_of_players += (
                f"\n-# Average MMR: {round( sum( [player.mmr for player in players] ) / len(players) )} \n"
                f"-# Highest MMR: {max_mmr_player.name}: {max_mmr_player.mmr} \n"
                f"-# Lowest MMR: {min_mmr_player.name}: {min_mmr_player.mmr} \n"
                if context == "mmr"
                else ""
            )

        message = await ctx.respond(
            list_of_players,
            ephemeral=ctx.mogi.vote,
            allowed_mentions=AllowedMentions.none(),
        )
        await message.edit(suppress=True)


def setup(bot: commands.Bot):
    bot.add_cog(list_mogi(bot))
