import os

import discord
from discord.ext import commands

from logger import setup_logger, highlight
from config import DISCORD_TOKEN, LOG_CHANNEL_ID

from utils.data.state import state_manager
from models.CustomMogiContext import MogiApplicationContext

logger = setup_logger(__name__)

intents = discord.Intents.all()


class YuzuLoungeBot(commands.Bot):
    """
    A custom Discord bot class for the Yuzu Lounge server.

    This class extends the `commands.Bot` class from the `discord.ext.commands` module.
    """

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    async def on_ready(self):
        logger.info(f"Logged into Discord")
        logger.info(f"Latency: {self.latency*1000:.2f}ms")
        print(
            f"""
            {highlight(self.user)}
            ID: {highlight(self.user.id)}
        """
        )
        state_manager.load_backup()
        await (await self.fetch_channel(LOG_CHANNEL_ID)).send("🟢 Bot is online!")

        print("Guilds:")
        for guild in self.guilds:
            print(guild.name)
        print("--------")

    async def get_application_context(self, interaction, cls=MogiApplicationContext):
        return await super().get_application_context(interaction, cls=cls)

    async def close(self):
        if channel := self.get_channel(LOG_CHANNEL_ID):
            await channel.send("🔄 Bot is shutting down...")
        for name, cog in self.cogs.items():
            cog._eject(self)
            print(f"Ejected {name}")
        await super().close()

    async def on_application_command(self, ctx: MogiApplicationContext):
        """Runs before every slash command"""
        # Defer the response to get 3 minutes instead of 30 seconds
        # await ctx.defer() this didn't turn out as a good idea


bot = YuzuLoungeBot(
    command_prefix=".",
    case_insensitive=True,
    help_command=None,
    intents=intents,
    status=discord.Status.online,
    activity=discord.Streaming(
        name="bytes for booting...", url="https://www.youtube.com/watch?v=xvFZjo5PgG0"
    ),
)


def main():
    print("----Loading extensions----")
    for root, dirs, files in os.walk("./cogs"):
        for file in files:
            if file.endswith(".py"):
                cog_path = os.path.join(root, file)
                extension = (
                    cog_path[2:].replace("/", ".").replace("\\", ".").replace(".py", "")
                )
                bot.load_extension(extension)
                print(f"Loaded {extension}")
    logger.debug("*Finished loading extensions*")

    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
