from discord.ext import commands

from logger import setup_logger, highlight
from utils.data.state import state_manager
from config import LOG_CHANNEL_ID

logger = setup_logger(__name__)


# BUG: can't i put this in main?
class ready(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"Logged into Discord")
        logger.info(f"Latency: {self.bot.latency*1000:.2f}ms")
        print(
            f"""
            {highlight(self.bot.user)}
            ID: {highlight(self.bot.user.id)}
        """
        )
        state_manager.load_backup()
        await (await self.bot.fetch_channel(LOG_CHANNEL_ID)).send("🟢 Bot is online!")

        print("Guilds:")
        for guild in self.bot.guilds:
            print(guild.name)
        print("--------")


def setup(bot: commands.Bot):
    bot.add_cog(ready(bot))
