from discord import slash_command, Option
from discord.ext import commands

from models import MogiApplicationContext, Guild

from utils.data import data_manager
from utils.command_helpers import guild_name_autocomplete


class guild(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(
        name="guild",
        description="View your guild or a guild of your choice",
    )
    async def guild(
        self,
        ctx: MogiApplicationContext,
        searched_name: str = Option(
            str, "Name", required=False, autocomplete=guild_name_autocomplete
        ),
    ):
        await ctx.defer()

        potential_guild: Guild | None = data_manager.Guilds.find(
            query=searched_name if searched_name else ctx.user.id
        )

        if potential_guild:
            return await ctx.respond(potential_guild.__repr__)

        return await ctx.respond(
            f"Couldn't find {'that' if searched_name else 'your'} guild."
        )


def setup(bot: commands.Bot):
    bot.add_cog(guild(bot))
