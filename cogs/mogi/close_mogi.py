from discord import slash_command
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from utils.data.mogi_manager import mogi_manager
from utils.command_helpers.confirm import confirmation
from utils.command_helpers.checks import is_mogi_not_in_progress


class close_mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="close", description="Close a mogi")
    @is_mogi_not_in_progress()
    async def close(self, ctx: MogiApplicationContext):
        await ctx.interaction.response.defer()

        close_confirm_message = "{} don't close the mogi unless it fully finished. \nClosing will remove all players and discard any points.\n **Are you sure?**".format(
            ctx.author.mention
        )

        if await confirmation(ctx, close_confirm_message):
            mogi_manager.destroy_mogi(ctx.channel.id)
            return await ctx.respond("# This channel's Mogi has been closed.")

        await ctx.respond("Cancelled.")


def setup(bot: commands.Bot):
    bot.add_cog(close_mogi(bot))
