from discord import ApplicationContext, slash_command
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
        return await ctx.respond("The bot couldn't start up properly. The admins are notified and will fix this in just a few minutes.")
    
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

def setup(bot: commands.Bot):
    bot.add_cog(safemode_cog(bot))
