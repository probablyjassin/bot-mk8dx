from discord import Option, AllowedMentions, SlashCommandGroup, Member
from discord.ext import commands

from models.PlayerModel import PlayerProfile
from models.CustomMogiContext import MogiApplicationContext

from utils.data.data_manager import data_manager
from utils.data.mogi_manager import mogi_manager
from utils.maths.replace import recurse_replace
from utils.decorators.player import with_player
from utils.command_helpers.find_player import get_guild_member
from utils.decorators.checks import (
    is_mogi_open,
    is_mogi_in_progress,
    is_mogi_not_in_progress,
    is_mogi_not_full,
    is_mogi_manager,
    is_moderator,
    is_admin,
)


class managing(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    manage = SlashCommandGroup(
        "manage", "Commands for mogi managers to manage players and such."
    )

    @manage.command(name="add", description="Add a player to the current mogi")
    @is_moderator()
    @is_mogi_not_in_progress()
    @is_mogi_not_full()
    @with_player(
        query_varname="player", assert_not_in_mogi=True, assert_not_suspended=True
    )
    async def add_player(
        self,
        ctx: MogiApplicationContext,
        player: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
    ):
        # Add to mogi and add roles
        ctx.mogi.players.append(ctx.player)
        if ctx.player_discord and ctx.inmogi_role not in ctx.player_discord.roles:
            await ctx.player_discord.add_roles(ctx.inmogi_role, reason="Added to Mogi")

        await ctx.respond(
            f"<@{ctx.player.discord_id}> joined the mogi! (against their will)"
        )

    @manage.command(name="remove", description="Remove a player from the current mogi")
    @is_mogi_manager()
    @is_mogi_not_in_progress()
    @with_player(query_varname="player", assert_in_mogi=True)
    async def remove(
        self,
        ctx: MogiApplicationContext,
        player: str = Option(
            str, name="player", description="The player to remove from the mogi."
        ),
    ):
        ctx.mogi.players.remove(player)

        # remove the role
        if ctx.player_discord and ctx.inmogi_role in ctx.player_discord.roles:
            await ctx.player_discord.remove_roles(
                ctx.inmogi_role, reason="Removed from Mogi"
            )

        await ctx.respond(
            f"<@{ctx.player.discord_id}> was removed from the mogi.",
        )

    @manage.command(
        name="sub", description="Substitute a player who can't play anymore."
    )
    @is_mogi_manager()
    @is_mogi_in_progress()
    @with_player(
        query_varname="player_name", assert_in_mogi=True, assert_not_suspended=True
    )
    async def sub(
        self,
        ctx: MogiApplicationContext,
        player_name: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
        replacement_name: str = Option(
            str, name="sub", description="username | @ mention | discord_id"
        ),
    ):
        replacement_profile = data_manager.find_player(replacement_name)

        if not replacement_profile:
            return await ctx.respond("Sub profile not found", ephemeral=True)

        # Check if replacement is in a mogi in another channel
        for mogi in mogi_manager.mogi_registry.values():
            if replacement_profile in mogi.players:
                if mogi.channel_id == ctx.channel_id:
                    return await ctx.respond("Sub is already in the mogi.")
                return await ctx.respond(
                    f"The player to sub is already in a mogi in <#{mogi.channel_id}>"
                )

        ctx.mogi.players = recurse_replace(
            ctx.mogi.players, ctx.player, replacement_profile
        )
        ctx.mogi.teams = recurse_replace(
            ctx.mogi.teams, ctx.player, replacement_profile
        )

        ctx.mogi.subs.append(replacement_profile)

        if ctx.player_discord and ctx.inmogi_role in ctx.player_discord.roles:
            await ctx.player_discord.remove_roles(ctx.inmogi_role, reason="Subbed out")

        replacement_user: Member | None = await get_guild_member(
            ctx.guild, replacement_profile.discord_id
        )
        if replacement_user and ctx.inmogi_role not in replacement_user.roles:
            await replacement_user.add_roles(ctx.inmogi_role, reason="Subbed in")

        await ctx.respond(
            f"<@{ctx.player.discord_id}> has been subbed out for <@{replacement_profile.discord_id}>"
        )

    @manage.command(
        name="swap",
        description="Swap two players in the mogi with one another (for teams)",
    )
    @is_admin()
    @is_mogi_open()
    async def swap(
        self,
        ctx: MogiApplicationContext,
        player1: str = Option(str, name="player1", description="first player"),
        player2: str = Option(str, name="player2", description="second player"),
    ):
        first_player: PlayerProfile | str = data_manager.find_player(player1) or player1
        second_player: PlayerProfile | str = (
            data_manager.find_player(player2) or player2
        )
        for player in [first_player, second_player]:
            if isinstance(player, str):
                return await ctx.respond(f"{player} not found")
            if player not in ctx.mogi.players:
                return await ctx.send(f"<@{player.discord_id}> not in the mogi")

        ctx.mogi.players = recurse_replace(ctx.mogi.players, first_player, None)
        ctx.mogi.players = recurse_replace(
            ctx.mogi.players, second_player, first_player
        )
        ctx.mogi.players = recurse_replace(ctx.mogi.players, None, second_player)

        ctx.mogi.teams = recurse_replace(ctx.mogi.teams, first_player, None)
        ctx.mogi.teams = recurse_replace(ctx.mogi.teams, second_player, first_player)
        ctx.mogi.teams = recurse_replace(ctx.mogi.teams, None, second_player)

        await ctx.respond(f"Swapped {first_player.name} with {second_player.name}")

    @manage.command(
        name="remove_sub",
        description="Remove a player from the sub list. Will let them lose MMR.",
    )
    @is_mogi_in_progress()
    @is_moderator()
    @with_player(query_varname="player_name")
    async def remove_sub(
        self,
        ctx: MogiApplicationContext,
        player_name: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
    ):
        if ctx.player not in ctx.mogi.subs:
            return await ctx.respond("Player not in the sub list", ephemeral=True)

        ctx.mogi.subs.remove(ctx.player)

        await ctx.respond(
            f"<@{ctx.player.discord_id}> won't be listed as sub.",
            allowed_mentions=AllowedMentions.none(),
        )

    @manage.command(name="add_sub", description="Add a player to the sub list.")
    @is_mogi_in_progress()
    @is_moderator()
    @with_player(query_varname="player_name")
    async def add_sub(
        self,
        ctx: MogiApplicationContext,
        player_name: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
    ):
        if ctx.player in ctx.mogi.subs:
            return await ctx.respond("Player already in the sub list", ephemeral=True)

        ctx.mogi.subs.append(ctx.player)

        await ctx.respond(
            f"<@{ctx.player.name}> is now listed as sub.",
            allowed_mentions=AllowedMentions.none(),
        )


def setup(bot: commands.Bot):
    bot.add_cog(managing(bot))
