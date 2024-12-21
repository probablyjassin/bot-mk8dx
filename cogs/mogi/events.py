from discord import slash_command, Option, SlashCommandGroup
from discord.ext import commands

from pymongo import UpdateOne

from models.CustomMogiContext import MogiApplicationContext

from utils.data.database import db_players
from utils.command_helpers.checks import is_mogi_open, is_moderator


class events(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    event = SlashCommandGroup(name="event", description="Event commands")

    @event.command(
        name="give_mmr", description="Give MMR to all players in the current mogi"
    )
    @is_moderator()
    @is_mogi_open()
    async def give_mmr(
        self,
        ctx: MogiApplicationContext,
        amount: int = Option(int, "amount of mmr to give"),
    ):
        if len(ctx.mogi.players) == 0:
            return await ctx.respond("No players in the mogi")

        await ctx.defer()

        all_player_names = [player.name for player in ctx.mogi.players]
        all_player_mmrs = [player.mmr for player in ctx.mogi.players]
        all_player_new_mmrs = [
            all_player_mmrs[i] + amount for i in range(len(ctx.mogi.players))
        ]

        data_to_update_obj = [
            {
                "name": all_player_names[i],
                "new_mmr": all_player_new_mmrs[i],
                "delta": amount,
            }
            for i in range(len(all_player_names))
        ]

        db_players.bulk_write(
            [
                UpdateOne(
                    {"name": entry["name"]},
                    {
                        "$set": {
                            "mmr": entry["new_mmr"] if entry["new_mmr"] > 0 else 1
                        },
                        "$push": {"history": entry["delta"]},
                    },
                    upsert=False,
                )
                for entry in data_to_update_obj
            ]
        )

        await ctx.respond(f"{amount} MMR given to all players")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(events(bot))
