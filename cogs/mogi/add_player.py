from discord import slash_command, Message
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from utils.command_helpers.checks import is_mogi_not_in_progress


class add_player(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="add", description="Add a player to the current mogi")
    @is_mogi_not_in_progress()
    async def add_player(self, ctx: MogiApplicationContext):

        # user already in the mogi
        if ctx.inmogi_role in ctx.user.roles:
            return await ctx.respond("You are already in the mogi", ephemeral=True)

        ctx.mogi.add_player(ctx.user)
        await ctx.respond(f"{ctx.user.mention} has been added to the mogi")


def setup(bot: commands.Bot):
    bot.add_cog(add_player(bot))
