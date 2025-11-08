from discord import SlashCommandGroup, Option
from discord.ext import commands

from models import MogiApplicationContext
from utils.decorators import is_moderator, with_player


class archive(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    archive = SlashCommandGroup(
        name="archive", description="Archive or unarchive players"
    )

    @archive.command(name="add", description="Archive a player")
    @is_moderator()
    @with_player(query_varname="searched_player")
    async def archive_add(
        self,
        ctx: MogiApplicationContext,
        searched_player: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
    ):
        if ctx.player.inactive:
            return await ctx.respond(f"{ctx.player.name} is already archived")

        await ctx.player.set_inactive(True)

        await ctx.respond(f"Archived <@{ctx.player.discord_id}>")

    @archive.command(name="retrieve", description="Unarchive a player")
    @is_moderator()
    @with_player(query_varname="searched_player")
    async def archive_retrieve(
        self,
        ctx: MogiApplicationContext,
        searched_player: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
    ):
        if not ctx.player.inactive:
            return await ctx.respond(f"{ctx.player.name} is already not archived")
        await ctx.player.set_inactive(False)

        await ctx.respond(f"Retrieved <@{ctx.player.discord_id}>")


def setup(bot: commands.Bot):
    bot.add_cog(archive(bot))
