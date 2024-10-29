import random

from discord import SlashCommandGroup, ApplicationContext
from discord.ext import commands

from models.MogiModel import Mogi
from models.PlayerModel import PlayerProfile
from utils.data.mogi_manager import mogi_manager


class debugging(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    debug = SlashCommandGroup(name="debug", description="Debugging commands")

    @debug.command(name="current_mogi", description="print the mogi for this channel")
    async def current_mogi(self, ctx: ApplicationContext):
        mogi = mogi_manager.get_mogi(ctx.channel.id)
        await ctx.respond(f"Current Mogi: \n{mogi}")

    @debug.command(name="all_mogis", description="print the mogi registry")
    async def all_mogis(self, ctx: ApplicationContext):
        await ctx.respond(f"Mogi Registry: \n{mogi_manager.read_registry()}")

    @debug.command(name="throw_error", description="throw an error")
    async def throw_error(self, ctx: ApplicationContext):
        raise Exception("This is a test command error")

    @debug.command(name="test_player", description="add a dummy player to the mogi")
    async def test_player(self, ctx: ApplicationContext):
        mogi: Mogi = mogi_manager.get_mogi(ctx.channel.id)

        dummy_names = ["spamton", "jordan", "mrboost", "bruv"]
        dummy: PlayerProfile = PlayerProfile(
            _id=0,
            name=f"{random.choice(dummy_names)}{str(random.randint(10, 99))}",
            mmr=random.randint(1000, 6000),
            discord_id=000000000000000000,
            history=[],
        )
        mogi.players.append(dummy)
        await ctx.respond(f"Added {dummy.name} to the mogi")


def setup(bot: commands.Bot):
    bot.add_cog(debugging(bot))
