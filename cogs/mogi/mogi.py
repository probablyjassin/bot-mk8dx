from discord import slash_command
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from utils.data.mogi_manager import mogi_manager
from utils.command_helpers.confirm import confirmation
from utils.command_helpers.checks import is_mogi_not_in_progress


class mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="open", description="Open a mogi")
    async def open(self, ctx: MogiApplicationContext):
        try:
            mogi_manager.create_mogi(ctx.channel.id)
            await ctx.respond("# Started a new mogi! \n Use /join to participate!")
        except ValueError:
            await ctx.respond("A Mogi for this channel is already open.")

    @slash_command(name="close", description="Close a mogi")
    @is_mogi_not_in_progress()
    async def close(self, ctx: MogiApplicationContext):
        await ctx.interaction.response.defer()

        close_confirm_message = "{} don't close the mogi unless it fully finished. \nClosing will remove all players and discard any points.\n **Are you sure?**".format(
            ctx.author.mention
        )

        if await confirmation(ctx, close_confirm_message):
            for player in ctx.mogi.players:
                (await ctx.guild.fetch_member(player.discord_id)).remove_roles(
                    ctx.inmogi_role
                )

            mogi_manager.destroy_mogi(ctx.mogi.channel_id)
            return await ctx.respond("# This channel's Mogi has been closed.")

        await ctx.respond("Cancelled.")


def setup(bot: commands.Bot):
    bot.add_cog(mogi(bot))
