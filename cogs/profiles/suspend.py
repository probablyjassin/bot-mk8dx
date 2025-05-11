from discord import SlashCommandGroup, Option
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from models.PlayerModel import PlayerProfile

from utils.command_helpers.find_player import search_player
from utils.decorators.checks import is_moderator


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
        player: PlayerProfile = search_player(searched_player, with_archived=True)

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
        player: PlayerProfile = search_player(searched_player, with_archived=True)

        if not player:
            await ctx.respond("Couldn't find that player")

        player.suspended = False

        await ctx.respond(f"Unsuspended <@{player.discord_id}>")


def setup(bot: commands.Bot):
    bot.add_cog(suspend(bot))
