from discord import slash_command
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext

from utils.decorators.checks import is_mogi_in_progress
from utils.decorators.player import with_player
from utils.decorators.checks import LoungeRole, _is_at_least_role


class password(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # WIP
    @slash_command(
        name="password", description="Get the password for the server your mogi uses."
    )
    @is_mogi_in_progress()
    @with_player(assert_in_mogi=True)
    async def password(self, ctx: MogiApplicationContext):
        if not ctx.mogi.room:
            return await ctx.respond(
                "This mogi doesn't have a server for it yet. Something might have gone wrong, ask a Mogi Manager."
            )

        if _is_at_least_role(ctx, LoungeRole.MOGI_MANAGER):
            return await ctx.respond(
                "Not implemented yet, but you are at least a mogi manager and should get all passwords.",
                ephemeral=True,
            )
        await ctx.respond(
            "Not implemented yet, but if you read this, all requirements are met for you to see the password.",
            ephemeral=True,
        )


def setup(bot: commands.Bot):
    bot.add_cog(password(bot))
