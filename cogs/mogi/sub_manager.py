from discord import SlashCommandGroup, Option, ApplicationContext
from discord.ext import commands

from models.PlayerModel import PlayerProfile
from models.MogiModel import Mogi

from utils.command_helpers.find_player import search_player
from utils.data.mogi_manager import mogi_manager
from utils.data.database import db_players
from utils.command_helpers.checks import (
    is_mogi_open,
    is_mogi_in_progress,
    is_mogi_manager,
)


def recurse_replace(space, player, sub):
    if isinstance(space, list):
        return [recurse_replace(item, player, sub) for item in space]
    else:
        return sub if space == player else space


class sub_manager(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    replacement = SlashCommandGroup(
        name="replacement", description="Substitute a player"
    )

    @replacement.command(name="sub")
    @is_mogi_manager()
    @is_mogi_in_progress()
    @is_mogi_open()
    async def sub(
        self,
        ctx: ApplicationContext,
        player_name: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
        replacement_name: str = Option(
            str, name="sub", description="username | @ mention | discord_id"
        ),
    ):
        mogi: Mogi = mogi_manager.get_mogi(ctx.channel.id)

        player_profile = search_player(player_name)
        replacement_profile = search_player(replacement_name)

        if not player_profile:
            return await ctx.respond("Player profile not found", ephemeral=True)

        if not replacement_profile:
            return await ctx.respond("Sub profile not found", ephemeral=True)

        if player_profile not in mogi.players:
            return await ctx.respond("Player not in the mogi", ephemeral=True)

        if replacement_profile in mogi.players:
            return await ctx.respond("Sub is already in the mogi.", ephemeral=True)

        mogi.players = recurse_replace(
            mogi.players, player_profile, replacement_profile
        )
        mogi.teams = recurse_replace(mogi.teams, player_profile, replacement_profile)

        mogi.subs.append(replacement_profile)

        await ctx.respond(
            f"<@{player_profile.discord_id}> has been subbed out for <@{replacement_profile.discord_id}>"
        )

    @replacement.command(
        name="remove_sub",
        description="Remove a player from the sub list. Will let them lose MMR.",
    )
    @is_mogi_manager()
    @is_mogi_in_progress()
    @is_mogi_open()
    async def remove_sub(
        self,
        ctx: ApplicationContext,
        player_name: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
    ):
        mogi: Mogi = mogi_manager.get_mogi(ctx.channel.id)

        player_profile = search_player(player_name)

        if not player_profile:
            return await ctx.respond("Player profile not found", ephemeral=True)

        if player_profile not in mogi.subs:
            return await ctx.respond("Player not in the sub list", ephemeral=True)

        mogi.subs.remove(player_profile)

        await ctx.respond(f"{player_profile.name} won't be listed as sub.")

    @replacement.command(name="add_sub", description="Add a player to the sub list.")
    @is_mogi_manager()
    @is_mogi_in_progress()
    @is_mogi_open()
    async def add_sub(
        self,
        ctx: ApplicationContext,
        player_name: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
    ):
        mogi: Mogi = mogi_manager.get_mogi(ctx.channel.id)

        player_profile = search_player(player_name)

        if not player_profile:
            return await ctx.respond("Player profile not found", ephemeral=True)

        if player_profile in mogi.subs:
            return await ctx.respond("Player already in the sub list", ephemeral=True)

        mogi.subs.append(player_profile)

        await ctx.respond(f"{player_profile.name} is now listed as sub.")


def setup(bot: commands.Bot):
    bot.add_cog(sub_manager(bot))
