from discord import slash_command, Option, SlashCommandGroup
from discord.ext import commands

import pymongo
from pymongo import UpdateOne

from models.CustomMogiContext import MogiApplicationContext

from utils.data.database import db_players

event = SlashCommandGroup(name="event", description="Event commands")


class events(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @event.command(
        name="give_mmr", description="Give MMR to all players in the current mogi"
    )
    async def give_mmr(
        self,
        ctx: MogiApplicationContext,
        amount: int = Option(int, "amount of mmr to give"),
    ):
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
