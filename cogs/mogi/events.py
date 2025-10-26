from discord import Option, SlashCommandGroup
from discord.ext import commands

from models import MogiApplicationContext

from utils.data import data_manager
from utils.decorators.checks import is_mogi_open, is_moderator


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

        data_manager.bulk_add_mmr([player.name for player in ctx.mogi.players], amount)

        await ctx.respond(f"{amount} MMR given to all players")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(events(bot))
