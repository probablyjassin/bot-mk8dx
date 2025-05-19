from discord import ApplicationContext, slash_command, SlashCommandGroup
from discord.ext import commands
from discord.utils import get

from config import LOG_CHANNEL_ID


class safemode_cog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Safe Mode is ready.")
        log_channel = await self.bot.fetch_channel(LOG_CHANNEL_ID)
        await log_channel.send("⚠️Bot failed to start up. Safe Mode is active.")
        await log_channel.send(get(log_channel.guild.roles, name="Admin").mention)

    @commands.Cog.listener()
    async def on_application_command(self, ctx: ApplicationContext):
        return await ctx.respond(
            "The bot couldn't start up properly. The admins are notified and will fix this in just a few minutes."
        )

    # Catch common commands to prevent 'unknown interaction' error
    @slash_command(name="join")
    async def join(self, ctx: ApplicationContext):
        return

    @slash_command(name="open")
    async def open(self, ctx: ApplicationContext):
        return

    @slash_command(name="close")
    async def close(self, ctx: ApplicationContext):
        return

    @slash_command(name="leave")
    async def leave(self, ctx: ApplicationContext):
        return

    @slash_command(name="l")
    async def l(self, ctx: ApplicationContext):
        return

    @slash_command(name="register")
    async def register(self, ctx: ApplicationContext):
        return

    manage = SlashCommandGroup(
        "manage", "Commands for mogi managers to manage players and such."
    )

    @manage.command(name="add")
    async def add(self, ctx: ApplicationContext):
        return

    @manage.command(name="remove")
    async def remove(self, ctx: ApplicationContext):
        return

    @manage.command(name="sub")
    async def sub(self, ctx: ApplicationContext):
        return

    @manage.command(name="swap")
    async def swap(self, ctx: ApplicationContext):
        return

    @manage.command(name="remove_sub")
    async def remove_sub(self, ctx: ApplicationContext):
        return

    @manage.command(name="add_sub")
    async def add_sub(self, ctx: ApplicationContext):
        return

    @slash_command(name="tax")
    async def tax(self, ctx: ApplicationContext):
        return

    @slash_command(name="move")
    async def move(self, ctx: ApplicationContext):
        return

    @slash_command(name="flags")
    async def flags(self, ctx: ApplicationContext):
        return

    suspension = SlashCommandGroup(
        name="suspension", description="Suspend or unsuspend players"
    )

    @suspension.command(name="add")
    async def add(self, ctx: ApplicationContext):
        return

    @suspension.command(name="remove")
    async def remove(self, ctx: ApplicationContext):
        return

    points = SlashCommandGroup(
        name="points", description="Commands for point collection and mmr calculation."
    )

    @points.command(name="collect")
    async def collect(self, ctx: ApplicationContext):
        return

    @points.command(name="reset")
    async def reset(self, ctx: ApplicationContext):
        return

    @points.command(name="apply")
    async def apply(self, ctx: ApplicationContext):
        return

    event = SlashCommandGroup(name="event", description="Event commands")

    @event.command(
        name="give_mmr", description="Give MMR to all players in the current mogi"
    )
    async def give_mmr(self, ctx: ApplicationContext):
        return

    archive = SlashCommandGroup(
        name="archive", description="Archive or unarchive players"
    )

    @archive.command(name="add", description="Archive a player")
    async def archive_add(
        self,
        ctx: ApplicationContext,
    ):
        return

    @archive.command(name="retrieve", description="Unarchive a player")
    async def archive_retrieve(
        self,
        ctx: ApplicationContext,
    ):
        return

    debug = SlashCommandGroup(name="debug", description="Debugging commands")

    @debug.command(name="current_mogi", description="print the mogi for this channel")
    async def current_mogi(self, ctx: ApplicationContext):
        return

    edit = SlashCommandGroup(name="edit", description="Suspend or unsuspend players")

    @edit.command(name="add_mmr", description="Add MMR to a player")
    async def add_mmr(
        self,
        ctx: ApplicationContext,
    ):
        return

    @slash_command(name="room", description="Get info on people playing on EU Main")
    async def room(self, ctx: ApplicationContext):
        return


def setup(bot: commands.Bot):
    bot.add_cog(safemode_cog(bot))
