from discord import slash_command, Option
from discord.utils import get
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from models.PlayerModel import PlayerProfile

from utils.command_helpers.find_player import search_player
from utils.decorators.checks import LoungeRole, _is_at_least_role

from config import REGISTER_CHANNEL_ID


class password(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # WIP
    @slash_command(
        name="password", description="Get the password for the server your mogi uses."
    )
    async def password(self, ctx: MogiApplicationContext):
        if not ctx.mogi:
            return await ctx.respond("There is no open mogi in this channel.")

        player: PlayerProfile | None = search_player(ctx.interaction.user.id)
        if not player:
            return await ctx.respond(
                f"Couldn't find your player profile, make sure you're registered in <#{REGISTER_CHANNEL_ID}> or contact a moderator."
            )
        if player not in ctx.mogi.players:
            return await ctx.respond(
                f"You're not in this mogi. If it hasn't started yet, you can join. <#{REGISTER_CHANNEL_ID}>"
            )

        if not ctx.mogi.isPlaying:
            return await ctx.respond("The mogi hasn't started yet.")
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
