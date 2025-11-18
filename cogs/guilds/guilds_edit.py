import re, string

from discord import SlashCommandGroup, Option
from discord.ext import commands
from discord.utils import get

from utils.data import data_manager
from models import MogiApplicationContext
from utils.decorators import with_guild, with_player, is_moderator
from utils.command_helpers import player_name_autocomplete, confirmation


class guilds_edit(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    guildedit = SlashCommandGroup(
        name="guildedit", description="Commands for Guild owners"
    )

    # Available for a limited time: Leaving the current guild
    @guildedit.command(
        name="leave",
        description="Leave your current guild to join a different one (temporarily available)",
    )
    @with_guild()
    async def leave(self, ctx: MogiApplicationContext):
        lounge_guild_role = get(
            ctx.guild.roles,
            name=f"GUILD | {ctx.lounge_guild.name}",
        )

        if lounge_guild_role in ctx.user.roles:
            await ctx.user.remove_roles(lounge_guild_role)

        if (
            general_guilds_role := get(ctx.guild.roles, name="Guilds")
        ) and general_guilds_role in ctx.player_discord.roles:
            await ctx.player_discord.remove_roles(general_guilds_role)

        await data_manager.Guilds.remove_member(ctx.lounge_guild, ctx.user.id)
        await ctx.respond(
            f"{ctx.user.mention} left the guild **{ctx.lounge_guild.name}**."
        )

    @guildedit.command(
        name="change-name",
        description="Change the name of your guild",
    )
    @with_guild(assert_is_owner=True)
    async def change_name(self, ctx: MogiApplicationContext, name: str = Option(str)):
        if len(name) < 3 or len(name) > 32:
            return await ctx.respond(
                "Guild name has to be between 3 and 32 characters long"
            )
        if name in await data_manager.Guilds.get_all_guild_names():
            return await ctx.respond("There already exists a guild with this name.")

        allowed_chars = string.ascii_letters + string.digits + " -_"
        if not all(char in allowed_chars for char in name):
            return await ctx.respond(
                "Guild name can only contain letters, numbers, spaces, hyphens, and underscores.",
                ephemeral=True,
            )

        lounge_guild_role = get(
            ctx.guild.roles,
            name=f"GUILD | {ctx.lounge_guild.name}",
        )

        await data_manager.Guilds.set_attribute(ctx.lounge_guild, "name", name)

        if lounge_guild_role:
            await lounge_guild_role.edit(name=f"GUILD | {name}")

        return await ctx.respond(f"Changed the name of your guild to `{name}`")

    @guildedit.command(name="icon", description="Change the guild icon.")
    @with_guild(assert_is_owner=True)
    async def icon(self, ctx: MogiApplicationContext, new_icon: str = Option(str)):
        if not re.match(
            r"^https?://.*\.(png|jpg|jpeg|gif|webp)$", new_icon, re.IGNORECASE
        ):
            return await ctx.respond(
                "Invalid image URL. Please provide a valid URL "
                "ending in .png, .jp(e)g, .gif, or .webp",
            )

        await data_manager.Guilds.set_attribute(ctx.lounge_guild, "icon", new_icon)
        return await ctx.respond(f"Changed your guild icon to: {new_icon}")

    @guildedit.command(name="add-member", description="Invite a member to your guild")
    @with_guild(assert_is_owner=True)
    @with_player(query_varname="player")
    async def add_member(
        self,
        ctx: MogiApplicationContext,
        player: str = Option(
            str,
            name="player",
            description="The Lounge Player to add",
            required=True,
            autocomplete=player_name_autocomplete,
        ),
    ):
        await ctx.response.defer()

        if len(ctx.lounge_guild.player_ids) >= 12:
            return await ctx.respond("Your guild is maxed out on players (12).")

        if existing_guild := await ctx.player.fetch_guild():
            return await ctx.respond(
                f"That player is already in the guild **{existing_guild.name}**."
            )

        if await confirmation(
            ctx,
            f"<@{ctx.player.discord_id}>, do you want to join the guild **{ctx.lounge_guild.name}**?",
            user_id=ctx.player.discord_id,
        ):
            lounge_guild_role = get(
                ctx.guild.roles,
                name=f"GUILD | {ctx.lounge_guild.name}",
            )

            await data_manager.Guilds.add_member(
                ctx.lounge_guild, ctx.player_discord.id
            )

            if lounge_guild_role:
                await ctx.player_discord.add_roles(lounge_guild_role)

            if (
                general_guilds_role := get(ctx.guild.roles, name="Guilds")
            ) and general_guilds_role not in ctx.player_discord.roles:
                await ctx.player_discord.add_roles(general_guilds_role)

            await ctx.respond(
                f"# <@{ctx.player_discord.id}> is now part of **{ctx.lounge_guild.name}**!"
            )
        else:
            await ctx.respond("The player rejected the invitation.")

    @guildedit.command(
        name="remove-member",
        description="MODS ONLY: Remove a player from their guild.",
    )
    @is_moderator()
    @with_player(query_varname="player")
    async def remove_member(
        self,
        ctx: MogiApplicationContext,
        player: str = Option(
            str,
            name="player",
            description="The Lounge Player to remove",
            required=True,
            autocomplete=player_name_autocomplete,
        ),
    ):
        await ctx.response.defer()

        if not (guild := await ctx.player.fetch_guild()):
            return await ctx.respond("That player is not in a guild.")

        lounge_guild_role = get(
            ctx.guild.roles,
            name=f"GUILD | {guild.name}",
        )

        await data_manager.Guilds.remove_member(guild, ctx.player.discord_id)

        if lounge_guild_role:
            await ctx.player_discord.remove_roles(lounge_guild_role)

        if (
            general_guilds_role := get(ctx.guild.roles, name="Guilds")
        ) and general_guilds_role in ctx.player_discord.roles:
            await ctx.player_discord.remove_roles(general_guilds_role)

        await ctx.respond(
            f"{ctx.player_discord.mention} has been removed from **{guild.name}**."
        )


def setup(bot: commands.Bot):
    bot.add_cog(guilds_edit(bot))
