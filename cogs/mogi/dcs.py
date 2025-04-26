from discord import Role, Message
from discord.utils import get
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext

from config import GUILD_IDS, LOG_CHANNEL_ID


class dcs(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self.inmogi_role: Role = get(
            get(self.bot.guilds, id=GUILD_IDS[0]), name="InMogi"
        )

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        if (
            message.content.lower().endswith("dc")
            and f"<#{self.inmogi_role.id}>" in message.content
        ):
            error_channel = await self.bot.fetch_channel(LOG_CHANNEL_ID)
            await error_channel.send(
                f"Test: @InMogi pinged in <#{message.channel.id}>: {message.content}"
            )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(dcs(bot))
