from discord import SlashCommandGroup, Option
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from models.PlayerModel import PlayerProfile

from utils.command_helpers.find_player import search_player
from utils.command_helpers.checks import is_mogi_manager, is_moderator


class disconnects(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    disconnects = SlashCommandGroup(
        name="disconnects", description="Add or set players amount of disconnects"
    )

    @disconnects.command(name="add", description="Add a DC to a player's count")
    @is_mogi_manager()
    async def disconnects_add(
        self,
        ctx: MogiApplicationContext,
        searched_player: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
    ):
        player = search_player(searched_player)

        if not player:
            return await ctx.respond("Couldn't find that player")

        if player in ctx.mogi.players:
            player: PlayerProfile = next(
                (
                    p
                    for p in ctx.mogi.players
                    if p.discord_id == searched_player
                    or p.name == searched_player.lower()
                ),
                None,
            )

        player.add_disconnect()

        await ctx.respond(
            f"Added a DC to <@{player.discord_id}> (now {player.disconnects})"
        )

    @disconnects.command(name="set", description="Set a player's DC count")
    @is_moderator()
    async def disconnects_set(
        self,
        ctx: MogiApplicationContext,
        searched_player: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
        amount: int = Option(int, name="amount", description="amount of disconnects"),
    ):
        player: PlayerProfile = next(
            (
                p
                for p in ctx.mogi.players
                if p.discord_id == searched_player
                or p.username.lower() == searched_player.lower()
            ),
            None,
        )
        if not player:
            player = search_player(searched_player)

        if not player:
            return await ctx.respond("Couldn't find that player")

        player.disconnects = amount

        await ctx.respond(
            f"Set <@{player.discord_id}>'s DC count to {player.disconnects}"
        )


def setup(bot: commands.Bot):
    bot.add_cog(disconnects(bot))
