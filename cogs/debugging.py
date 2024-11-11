import random
from bson import ObjectId

from discord import SlashCommandGroup
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from models.PlayerModel import PlayerProfile
from utils.data.mogi_manager import mogi_manager
from utils.command_helpers.checks import is_admin, is_mogi_not_in_progress


class debugging(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    debug = SlashCommandGroup(name="debug", description="Debugging commands")

    @debug.command(name="current_mogi", description="print the mogi for this channel")
    @is_admin()
    async def current_mogi(self, ctx: MogiApplicationContext):
        await ctx.respond(f"Current Mogi: \n{ctx.mogi}")

    @debug.command(name="all_mogis", description="print the mogi registry")
    @is_admin()
    async def all_mogis(self, ctx: MogiApplicationContext):
        await ctx.respond(f"Mogi Registry: \n{mogi_manager.read_registry()}")

    @debug.command(name="throw_error", description="throw an error")
    @is_admin()
    async def throw_error(self, ctx: MogiApplicationContext):
        raise Exception("This is a test command error")

    @debug.command(name="test_player", description="add a dummy player to the mogi")
    @is_mogi_not_in_progress()
    @is_admin()
    async def test_player(self, ctx: MogiApplicationContext):

        dummy_names = ["spamton", "jordan", "mrboost", "bruv"]
        dummy: PlayerProfile = PlayerProfile(
            _id=ObjectId("0123456789ab0123456789ab"),
            name=f"{random.choice(dummy_names)}{str(random.randint(10, 99))}",
            mmr=random.randint(1000, 6000),
            discord_id=000000000000000000,
            history=[],
        )
        ctx.mogi.players.append(dummy)
        await ctx.respond(f"Added {dummy.name} to the mogi")


def setup(bot: commands.Bot):
    bot.add_cog(debugging(bot))
