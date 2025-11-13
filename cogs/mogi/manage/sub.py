from typing import Literal

from discord import Option, AllowedMentions, SlashCommandGroup, Member
from discord.ext import commands
from discord.utils import get

from models import MogiApplicationContext

from utils.data import data_manager, mogi_manager
from utils.maths.replace import recurse_replace
from utils.command_helpers import get_guild_member, player_name_autocomplete
from utils.decorators import (
    is_mogi_in_progress,
    is_mogi_manager,
    is_moderator,
    with_player,
)


class sub(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    manage = SlashCommandGroup(
        "manage", "Commands for mogi managers to manage players and such."
    )

    @manage.command(
        name="sub", description="Substitute a player who can't play anymore."
    )
    @is_mogi_manager()
    @is_mogi_in_progress()
    async def sub(
        self,
        ctx: MogiApplicationContext,
        player_name: str = Option(
            str,
            name="player",
            description="username | @ mention | discord_id",
            autocomplete=player_name_autocomplete,
        ),
        replacement_name: str = Option(
            str,
            name="sub",
            description="username | @ mention | discord_id",
            autocomplete=player_name_autocomplete,
        ),
        reason: Literal[
            "DC'd twice or more", "Needs to go / disappeared / other"
        ] = Option(
            name="reason",
            description="Why is this person getting subbed?",
        ),
        no_tax: bool = Option(
            bool,
            name="no_tax",
            description="For example when they DCd from shaderbugs or power outages.",
            required=False,
        ),
    ):
        player_profile = await data_manager.Players.find(player_name)
        replacement_profile = await data_manager.Players.find(replacement_name)

        if not player_profile:
            return await ctx.respond("Player profile not found", ephemeral=True)

        if not replacement_profile:
            return await ctx.respond("Sub profile not found", ephemeral=True)

        if player_profile not in ctx.mogi.players:
            return await ctx.respond("Player to sub out is not in the mogi")

        # Check if replacement is in a mogi in another channel
        for mogi in mogi_manager.read_registry().values():
            if replacement_profile in mogi.players:
                if mogi.channel_id == ctx.channel_id:
                    return await ctx.respond("Sub is already in the mogi.")
                return await ctx.respond(
                    f"The player to sub is already in a mogi in <#{mogi.channel_id}>"
                )

        ctx.mogi.players = recurse_replace(
            ctx.mogi.players, player_profile, replacement_profile
        )
        ctx.mogi.teams = recurse_replace(
            ctx.mogi.teams, player_profile, replacement_profile
        )

        ctx.mogi.subs.append(replacement_profile)

        player_user: Member | None = await get_guild_member(
            ctx.guild, player_profile.discord_id
        )
        replacement_user: Member | None = await get_guild_member(
            ctx.guild, replacement_profile.discord_id
        )
        if player_user:
            if ctx.inmogi_role in player_user.roles:
                await player_user.remove_roles(ctx.inmogi_role, reason="Subbed out")

            all_team_roles = [
                get(ctx.guild.roles, name=f"Team {i+1}") for i in range(5)
            ]
            for role in all_team_roles:
                if role in player_user.roles:
                    player_user.remove_roles(role)
                    replacement_user.add_roles(role)

        if replacement_user and ctx.inmogi_role not in replacement_user.roles:
            await replacement_user.add_roles(ctx.inmogi_role, reason="Subbed in")

        await ctx.respond(
            f"<@{player_profile.discord_id}> has been subbed out for <@{replacement_profile.discord_id}>"
        )

        if not no_tax:
            tax = 50 if reason == "DC'd twice or more" else 100
            await player_profile.set_mmr(player_profile.mmr - tax)
            await ctx.channel.send(
                f"Penalized {player_user.mention} for leaving the mogi prematurely"
            )

    @manage.command(name="add_sub", description="Add a player to the sub list.")
    @is_mogi_in_progress()
    @is_moderator()
    @with_player(query_varname="player_name")
    async def add_sub(
        self,
        ctx: MogiApplicationContext,
        player_name: str = Option(
            str,
            name="player",
            description="username | @ mention | discord_id",
            autocomplete=player_name_autocomplete,
        ),
    ):
        if ctx.player in ctx.mogi.subs:
            return await ctx.respond("Player already in the sub list", ephemeral=True)

        ctx.mogi.subs.append(ctx.player)

        await ctx.respond(
            f"<@{ctx.player.name}> is now listed as sub.",
            allowed_mentions=AllowedMentions.none(),
        )

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
            str,
            name="player",
            description="username | @ mention | discord_id",
            autocomplete=player_name_autocomplete,
        ),
    ):
        if ctx.player not in ctx.mogi.subs:
            return await ctx.respond("Player not in the sub list", ephemeral=True)

        ctx.mogi.subs.remove(ctx.player)

        await ctx.respond(
            f"<@{ctx.player.discord_id}> won't be listed as sub.",
            allowed_mentions=AllowedMentions.none(),
        )


def setup(bot: commands.Bot):
    bot.add_cog(sub(bot))
