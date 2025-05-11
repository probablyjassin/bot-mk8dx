from discord import SlashCommandGroup, Option, AllowedMentions
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from models.PlayerModel import PlayerProfile

from utils.command_helpers.find_player import search_player
from utils.decorators.checks import is_mogi_manager, is_moderator

from utils.data.data_manager import data_manager, archive_type, player_field


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

        if ctx.mogi and player in ctx.mogi.players:
            player: PlayerProfile = next(
                (p for p in ctx.mogi.players if p.discord_id == player.discord_id),
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
        player = search_player(searched_player)

        if not player:
            return await ctx.respond("Couldn't find that player")

        if ctx.mogi and player in ctx.mogi.players:
            player: PlayerProfile = next(
                (p for p in ctx.mogi.players if p.discord_id == player.discord_id),
                None,
            )

        player.disconnects = amount

        await ctx.respond(
            f"Set <@{player.discord_id}>'s DC count to {player.disconnects}"
        )

    @disconnects.command(
        name="list", description="Show the top 3 players with the most DCs"
    )
    async def disconnects_list(self, ctx: MogiApplicationContext):

        players = sorted(
            list(
                data_manager.get_all_player_entries(
                    archive=archive_type.INCLUDE, only_field=player_field.DISCONNECTS
                )
            ),
            key=lambda p: p["disconnects"],
            reverse=True,
        )[:3]

        players_str = "\n".join(
            [
                f"<@{player['discord_id']}>: {player['disconnects']}"
                for player in players
            ]
        )

        await ctx.respond(
            f"Top 3 players with the most DCs: \n{players_str}",
            allowed_mentions=AllowedMentions.none(),
        )


def setup(bot: commands.Bot):
    bot.add_cog(disconnects(bot))
