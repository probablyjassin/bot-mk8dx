from discord import slash_command, Option, TextChannel, AllowedMentions
from discord.ext import commands

from models import MogiApplicationContext, PlayerProfile

from utils.data import mogi_manager
from services.players import find_player_profile
from utils.decorators import is_mogi_not_in_progress, is_mogi_open, is_admin
from utils.command_helpers import confirmation, remove_team_roles, get_guild_member


class mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.channels_pings = {}

    @slash_command(name="open", description="Open a mogi")
    async def open(self, ctx: MogiApplicationContext):
        try:
            mogi_manager.create_mogi(ctx.channel.id)
            await ctx.respond("# Started a new mogi! \n Use /join to participate!")
        except ValueError:
            message = "A Mogi for this channel is already open."
            if ctx.mogi and ctx.mogi.collected_points:
                message = "The points are still being worked on. The mogi will close on it's own when it's done."
            await ctx.respond(message)

    @slash_command(name="close", description="Close this channel's mogi")
    @is_mogi_not_in_progress()
    async def close(self, ctx: MogiApplicationContext):
        await ctx.interaction.response.defer()

        player: PlayerProfile | None = await find_player_profile(query=ctx.user.id)
        if not player:
            return await ctx.respond("Couldn't find your Profile")
        if (
            player not in ctx.mogi.players
            and ctx.get_lounge_role("Mogi Manager") not in ctx.user.roles
        ):
            return await ctx.respond("You're not in this mogi")

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

        current_mogi_channel_id: int = ctx.mogi.channel_id

        await ctx.send(f"<#{current_mogi_channel_id}> => {to_channel.mention}")

        all_mogis_dicts = mogi_manager.read_registry().items()
        all_mogis_dicts[to_channel.id] = all_mogis_dicts[current_mogi_channel_id]
        ctx.mogi.channel_id = to_channel.id
        del all_mogis_dicts[current_mogi_channel_id]
        await ctx.respond(
            f"# This mogi has been moved to <#{ctx.mogi.channel_id}>",
        )

    @slash_command(
        name="ping",
        description="Ping Lounge Players to gather players to join the mogi.",
    )
    @commands.cooldown(1, 900, commands.BucketType.channel)
    async def ping(
        self,
        ctx: MogiApplicationContext,
        need_sub: bool = Option(
            bool, description="use this when you're looking for a sub", required=False
        ),
        custom_message: str = Option(
            str,
            description="For mogi managers only. ''@LoungePlayer {custom_message}''",
            required=False,
        ),
    ):
        await ctx.defer(ephemeral=False)

        if not ctx.mogi:
            return await ctx.respond("No mogi open in this channel.")
        if not ctx.mogi.collected_points and ctx.mogi.isPlaying and not need_sub:
            return await ctx.respond(
                "The mogi is already in progress. If you're looking for a sub use need_sub=True"
            )

        lounge_player_role = ctx.get_lounge_role("Lounge Player")

        if custom_message and ctx.get_lounge_role("Mogi Manager") in ctx.user.roles:
            return await ctx.respond(
                f"# {lounge_player_role.mention} {custom_message}",
                allowed_mentions=AllowedMentions(roles=True),
            )

        if need_sub:
            return await ctx.respond(
                f"# {lounge_player_role.mention} we need a sub",
                allowed_mentions=AllowedMentions(roles=True),
            )

        return await ctx.respond(
            f"# {lounge_player_role.mention} {len(ctx.mogi.players)}/{ctx.mogi.player_cap} - join mogi",
            allowed_mentions=AllowedMentions(roles=True),
        )


def setup(bot: commands.Bot):
    bot.add_cog(mogi(bot))
