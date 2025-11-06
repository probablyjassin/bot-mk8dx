import string

from discord import SlashCommandGroup, Option
from discord.ext import commands

from utils.data import data_manager
from models import MogiApplicationContext
from utils.decorators import with_guild, with_player
from utils.command_helpers import player_name_autocomplete, confirmation


class guilds_edit(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    guildedit = SlashCommandGroup(
        name="guildedit", description="Commands for Guild owners"
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

        allowed_chars = string.ascii_letters + string.digits + " -_"
        if not all(char in allowed_chars for char in name):
            return await ctx.respond(
                "Guild name can only contain letters, numbers, spaces, hyphens, and underscores.",
                ephemeral=True,
            )

        data_manager.Guilds.set_attribute(ctx.lounge_guild, "name", name)
        if ctx.lounge_guild_role:
            ctx.lounge_guild_role.edit(name=f"GUILD | {name}")

        return await ctx.respond(f"Changed the name of your guild to `{name}`")

    @guildedit.command(name="add-member", description="Add a member to your guild")
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

        if existing_guild := data_manager.Guilds.get_player_guild(
            ctx.player.discord_id
        ):
            return await ctx.respond(
                f"That player is already in the guild **{existing_guild['name']}**."
            )

        if await confirmation(
            ctx,
            f"<@{ctx.player.discord_id}>, do you want to join the guild **{ctx.lounge_guild.name}**?",
            user_id=ctx.player.discord_id,
        ):
            data_manager.Guilds.add_member(ctx.lounge_guild, ctx.player.id)
            ctx.player_discord.add_roles(ctx.lounge_guild_role)
            await ctx.respond(
                f"<@{ctx.player.id}> is now part of **{ctx.lounge_guild.name}**!"
            )
        else:
            await ctx.respond("The player rejected the invitation.")


def setup(bot: commands.Bot):
    bot.add_cog(guilds_edit(bot))
