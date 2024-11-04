from discord import slash_command, Option, AllowedMentions
from discord.ext import commands

from models.PlayerModel import PlayerProfile
from models.CustomMogiContext import MogiApplicationContext

from utils.command_helpers.command_groups import manage
from utils.command_helpers.find_player import search_player
from utils.command_helpers.checks import is_mogi_not_in_progress


class kick(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @manage.command(name="remove")
    @is_mogi_not_in_progress()
    async def remove(
        self,
        ctx: MogiApplicationContext,
        player: str = Option(
            str, name="player", description="The player to remove from the mogi."
        ),
    ):
        player: PlayerProfile = search_player(player)
        if not player or player not in ctx.mogi.players:
            return await ctx.respond("Player not in mogi or not found.")

        ctx.mogi.players.remove(player)
        await ctx.interaction.user.remove_roles(ctx.inmogi_role)

        await ctx.respond(
            f"<@{player.discord_id}> got removed from the mogi.",
            allowed_mentions=AllowedMentions.none(),
        )


def setup(bot: commands.Bot):
    bot.add_cog(kick(bot))
