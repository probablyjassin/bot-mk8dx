from discord import slash_command, Option, SlashCommandGroup, Message
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext

from config import LOG_CHANNEL_ID


class dcs(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        if message.content.lower().endswith("dc"):
            error_channel = await self.bot.fetch_channel(LOG_CHANNEL_ID)
            await error_channel.send("Test: @InMogi pinged in a message")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(dcs(bot))
