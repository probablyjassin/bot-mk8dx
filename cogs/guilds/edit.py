import string

from discord import SlashCommandGroup, Option
from discord.ext import commands

from utils.data import data_manager
from models import MogiApplicationContext
from utils.decorators import with_guild


class edit(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    guildedit = SlashCommandGroup(
        name="guildedit", description="Commands for Guild owners"
    )

    @guildedit.command(
        name="change-name",
        description="Change the name of your guild",
    )
    @with_guild(assert_is_owner=True)
    async def change_name(self, ctx: MogiApplicationContext, name: str = Option(str)):
        if len(name) < 3 or len(name) > 32:
            return await ctx.respond(
                "Guild name has to be between 3 and 32 characters long"
            )

        allowed_chars = string.ascii_letters + string.digits + " -_"
        if not all(char in allowed_chars for char in name):
            return await ctx.respond(
                "Guild name can only contain letters, numbers, spaces, hyphens, and underscores.",
                ephemeral=True,
            )

        data_manager.Guilds.set_attribute(ctx.lounge_guild, "name", name)
        if ctx.lounge_guild_role:
            ctx.lounge_guild_role.edit(name=f"GUILD | {name}")

        return await ctx.respond(f"Changed the name of your guild to `{name}`")


def setup(bot: commands.Bot):
    bot.add_cog(edit(bot))
