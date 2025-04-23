from discord import Option, AllowedMentions, SlashCommandGroup
from discord.ext import commands

from models.PlayerModel import PlayerProfile
from models.CustomMogiContext import MogiApplicationContext

from utils.maths.replace import recurse_replace
from utils.command_helpers.find_player import search_player
from utils.command_helpers.checks import (
    is_mogi_in_progress,
    is_mogi_not_in_progress,
    is_mogi_manager,
    is_moderator,
)


class managing(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    manage = SlashCommandGroup(
        "manage", "Commands for mogi managers to manage players and such."
    )

    @manage.command(name="add", description="Add a player to the current mogi")
    @is_mogi_not_in_progress()
    @is_moderator()
    async def add_player(
        self,
        ctx: MogiApplicationContext,
        player: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
    ):
        player_profile: PlayerProfile = search_player(player)

        if not player_profile:
            return await ctx.respond("Player profile not found", ephemeral=True)

        # player already in the mogi
        if player_profile in ctx.mogi.players:
            return await ctx.respond("Player is already in the mogi", ephemeral=True)

        ctx.mogi.players.append(player_profile)
        await (await ctx.guild.fetch_member(player_profile.discord_id)).add_roles(
            ctx.inmogi_role
        )

        await ctx.respond(
            f"<@{player_profile.discord_id}> joined the mogi! (against their will)"
        )

    @manage.command(name="remove", description="Remove a player from the current mogi")
    @is_mogi_not_in_progress()
    @is_mogi_manager()
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

        # only try to edit roles if player is on server
        try:
            user = ctx.guild.fetch_member(player.discord_id)
            if not user:
                raise Exception("User not found")

            # remove the role
            await (await ctx.guild.fetch_member(player.discord_id)).remove_roles(
                ctx.inmogi_role
            )
        except Exception:
            await ctx.send(
                f"Player {player.name} not on this server anymore, skipping role removal."
            )

        await ctx.respond(
            f"<@{player.discord_id}> got removed from the mogi.",
            allowed_mentions=AllowedMentions.none(),
        )

    @manage.command(
        name="sub", description="Substitute a player who can't play anymore."
    )
    @is_mogi_in_progress()
    @is_mogi_manager()
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
        player_profile = search_player(player_name)
        replacement_profile = search_player(replacement_name)

        if not player_profile:
            return await ctx.respond("Player profile not found", ephemeral=True)

        if not replacement_profile:
            return await ctx.respond("Sub profile not found", ephemeral=True)

        if player_profile not in ctx.mogi.players:
            return await ctx.respond("Player not in the mogi", ephemeral=True)

        if replacement_profile in ctx.mogi.players:
            return await ctx.respond("Sub is already in the mogi.", ephemeral=True)

        ctx.mogi.players = recurse_replace(
            ctx.mogi.players, player_profile, replacement_profile
        )
        ctx.mogi.teams = recurse_replace(
            ctx.mogi.teams, player_profile, replacement_profile
        )

        ctx.mogi.subs.append(replacement_profile)

        await (await ctx.guild.fetch_member(player_profile.discord_id)).remove_roles(
            ctx.inmogi_role
        )
        await (await ctx.guild.fetch_member(replacement_profile.discord_id)).add_roles(
            ctx.inmogi_role
        )

        await ctx.respond(
            f"<@{player_profile.discord_id}> has been subbed out for <@{replacement_profile.discord_id}>"
        )

    @manage.command(
        name="remove_sub",
        description="Remove a player from the sub list. Will let them lose MMR.",
    )
    @is_mogi_in_progress()
    @is_moderator()
    async def remove_sub(
        self,
        ctx: MogiApplicationContext,
        player_name: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
    ):
        player_profile = search_player(player_name)

        if not player_profile:
            return await ctx.respond("Player profile not found", ephemeral=True)

        if player_profile not in ctx.mogi.subs:
            return await ctx.respond("Player not in the sub list", ephemeral=True)

        ctx.mogi.subs.remove(player_profile)

        await ctx.respond(
            f"<@{player_profile.discord_id}> won't be listed as sub.",
            allowed_mentions=AllowedMentions.none(),
        )

    @manage.command(name="add_sub", description="Add a player to the sub list.")
    @is_mogi_in_progress()
    @is_moderator()
    async def add_sub(
        self,
        ctx: MogiApplicationContext,
        player_name: str = Option(
            str, name="player", description="username | @ mention | discord_id"
        ),
    ):
        player_profile = search_player(player_name)

        if not player_profile:
            return await ctx.respond("Player profile not found", ephemeral=True)

        if player_profile in ctx.mogi.subs:
            return await ctx.respond("Player already in the sub list", ephemeral=True)

        ctx.mogi.subs.append(player_profile)

        await ctx.respond(
            f"<@{player_profile.name}> is now listed as sub.",
            allowed_mentions=AllowedMentions.none(),
        )


def setup(bot: commands.Bot):
    bot.add_cog(managing(bot))
