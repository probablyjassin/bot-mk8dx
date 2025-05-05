from discord import slash_command, Option, TextChannel
from discord.ext import commands
from discord.utils import get

from models.CustomMogiContext import MogiApplicationContext
from utils.data.mogi_manager import mogi_manager
from utils.command_helpers.confirm import confirmation
from utils.command_helpers.checks import is_mogi_not_in_progress, is_mogi_open, is_admin
from utils.command_helpers.team_roles import remove_team_roles
from utils.command_helpers.find_player import get_guild_member


class mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="open", description="Open a mogi")
    async def open(self, ctx: MogiApplicationContext):
        try:
            mogi_manager.create_mogi(ctx.channel.id)
            await ctx.respond("# Started a new mogi! \n Use /join to participate!")
        except ValueError:
            await ctx.respond("A Mogi for this channel is already open.")

    @slash_command(name="close", description="Close this channel's mogi")
    @is_mogi_not_in_progress()
    async def close(self, ctx: MogiApplicationContext):
        await ctx.interaction.response.defer()

        close_confirm_message = "{} don't close the mogi unless it fully finished. \nClosing will remove all players and discard any points.\n **Are you sure?**".format(
            ctx.author.mention
        )

        if await confirmation(ctx, close_confirm_message):
            for player in ctx.mogi.players:
                # only try to edit roles if player is on server
                user = await get_guild_member(ctx.guild, player.discord_id)
                if user and ctx.inmogi_role in user.roles:
                    await user.remove_roles(ctx.inmogi_role, reason="Mogi closed")

            mogi_manager.destroy_mogi(ctx.mogi.channel_id)

            # remove all team roles
            await remove_team_roles(ctx=ctx)
            return await ctx.respond("# This channel's Mogi has been closed.")

        await ctx.respond("Canceled")

    @slash_command(
        name="move", description="Move the current channel's mogi to another channel"
    )
    @is_mogi_open()
    @is_admin()
    async def move(
        self,
        ctx: MogiApplicationContext,
        to_channel: TextChannel = Option(
            TextChannel,
            name="to_channel",
            description="The channel to move the mogi to",
        ),
    ):
        await ctx.interaction.response.defer()

        if mogi_manager.get_mogi(to_channel.id):
            return await ctx.respond("A mogi in the target channel is already open")

        await ctx.send(ctx.mogi.channel_id)
        await ctx.send("current mogi id => new channel's id")
        ctx.mogi.channel_id = to_channel.id
        await ctx.respond(
            f"new current channel mogi id: {ctx.mogi.channel_id if ctx.mogi else 'no mogi here'}",
        )


def setup(bot: commands.Bot):
    bot.add_cog(mogi(bot))
