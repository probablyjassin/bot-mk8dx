from discord import SlashCommandGroup, Option, AllowedMentions
from discord.ext import commands

from models import MogiApplicationContext

from utils.decorators import is_mogi_manager, is_moderator, other_player

from utils.database.types import archive_type
from utils.data import data_manager


class disconnects(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    disconnects = SlashCommandGroup(
        name="disconnects", description="Add or set players amount of disconnects"
    )

    @disconnects.command(name="add", description="Add a DC to a player's count")
    @is_mogi_manager()
    @other_player(query_varname="searched_player")
    async def disconnects_add(
        self,
        ctx: MogiApplicationContext,
        searched_player: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
    ):
        if ctx.mogi and ctx.player in ctx.mogi.players:
            ctx.player = next(
                (p for p in ctx.mogi.players if p.discord_id == ctx.player.discord_id),
                None,
            )

        ctx.player.add_disconnect()

        await ctx.respond(
            f"Added a DC to <@{ctx.player.discord_id}> (now {ctx.player.disconnects})"
        )

    @disconnects.command(name="set", description="Set a player's DC count")
    @is_moderator()
    @other_player(query_varname="searched_player")
    async def disconnects_set(
        self,
        ctx: MogiApplicationContext,
        searched_player: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
        amount: int = Option(int, name="amount", description="amount of disconnects"),
    ):
        if ctx.mogi and ctx.player in ctx.mogi.players:
            ctx.player = next(
                (p for p in ctx.mogi.players if p.discord_id == ctx.player.discord_id),
                None,
            )

        ctx.player.disconnects = amount

        await ctx.respond(
            f"Set <@{ctx.player.discord_id}>'s DC count to {ctx.player.disconnects}"
        )

    @disconnects.command(
        name="list", description="Show the top 3 players with the most DCs"
    )
    async def disconnects_list(self, ctx: MogiApplicationContext):
        # Get all players and filter out those without disconnects field
        all_players = data_manager.Players.get_profiles(
            archive=archive_type.INCLUDE, as_json=True
        )
        players_with_dcs = [
            p
            for p in all_players
            if "disconnects" in p and p["disconnects"] is not None
        ]

        # Sort by disconnects count and take top 3
        players = sorted(
            players_with_dcs,
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
