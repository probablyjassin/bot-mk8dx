from discord import SlashCommandGroup, Option
from discord.ext import commands

from models import MogiApplicationContext, PlayerProfile

from utils.database.types import archive_type
from utils.data import data_manager
from utils.decorators import is_moderator


class suspend(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    suspension = SlashCommandGroup(
        name="suspension", description="Suspend or unsuspend players"
    )

    @suspension.command(name="add", description="Suspend a player")
    @is_moderator()
    async def suspend_add(
        self,
        ctx: MogiApplicationContext,
        searched_player: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
    ):
        player: PlayerProfile = await data_manager.Players.find(
            searched_player, archive=archive_type.INCLUDE
        )

        if not player:
            await ctx.respond("Couldn't find that player")

        player.suspended = True

        await ctx.respond(f"Suspended <@{player.discord_id}>")

    @suspension.command(name="remove", description="Unsuspend a player")
    @is_moderator()
    async def suspend_remove(
        self,
        ctx: MogiApplicationContext,
        searched_player: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
    ):
        player: PlayerProfile = await data_manager.Players.find(
            searched_player, archive=archive_type.INCLUDE
        )

        if not player:
            await ctx.respond("Couldn't find that player")

        player.suspended = False

        await ctx.respond(f"Unsuspended <@{player.discord_id}>")


def setup(bot: commands.Bot):
    bot.add_cog(suspend(bot))
