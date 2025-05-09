from discord import ApplicationContext
from discord.ext import commands

from config import LOG_CHANNEL_ID

class safemode_cog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Safe Mode is ready.")
        log_channel = await self.bot.fetch_channel(LOG_CHANNEL_ID)
        await log_channel.send("⚠️Bot failed to start up. Safe Mode is active.")

    @commands.Cog.listener()
    async def on_application_command(self, ctx: ApplicationContext):
        return await ctx.respond("The bot couldn't start up properly. The admins are notified and will fix this in just a few minutes.")

def setup(bot: commands.Bot):
    bot.add_cog(safemode_cog(bot))
