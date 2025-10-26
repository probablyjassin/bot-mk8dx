"""
Discord bot for the Yuzu Lounge server.
Used in competitive Mario Kart 8 Deluxe on the Yuzu Emulator.
Coordinates events to let players gather together and play.
"""

import os

import discord
from pycord.multicog import Bot

from logger import setup_logger, highlight
from cogs.error_handler import error_logger
from config import DISCORD_TOKEN, LOG_CHANNEL_ID

from utils.data.state import state_manager
from models import MogiApplicationContext


logger = setup_logger(__name__)


class YuzuLoungeBot(Bot):
    """
    A custom Discord bot class for the Yuzu Lounge server.

    This class extends the `commands.Bot` class from the `discord.ext.commands` module.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        logger.info("Logged into Discord")
        logger.info("Latency: %sms", self.latency * 1000)
        print(
            f"""
            {highlight(self.user)}
            ID: {highlight(self.user.id)}
        """
        )
        state_manager.load_saved()
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
    intents=discord.Intents.all(),
    status=discord.Status.online,
    activity=discord.Streaming(
        name="bytes for booting...", url="https://www.youtube.com/watch?v=xvFZjo5PgG0"
    ),
)


def load_cogs():
    """Load all cogs from the cogs directory."""
    print("----Loading extensions----")
    for root, _, files in os.walk("./cogs"):
        for file in files:
            if "cogs/guilds" in root.replace("\\", "/") and not file.endswith(
                ".cog.py"
            ):
                continue
            if file.endswith(".py"):
                cog_path = os.path.join(root, file)
                extension = (
                    cog_path[2:].replace("/", ".").replace("\\", ".").replace(".py", "")
                )
                try:
                    bot.load_extension(extension)
                    print(f"Loaded {extension}")
                except Exception as e:
                    print(f"Failed to load {extension}: {e}")
                    error_logger.error(f"Failed to load {extension}:{e}", exc_info=True)
                    raise
    logger.debug("*Finished loading extensions*")


def load_safe_mode():
    for name, cog in list(bot.cogs.items()):
        bot.unload_extension(cog.__module__)
        print(f"Unloaded {name}")
    try:
        bot.load_extension("utils.command_helpers.safemode_cog")
        logger.info("Loaded safemode_cog successfully.")
    except Exception as e:
        logger.error("Failed to load safemode_cog: %s", e)
        error_logger.error("Failed to load safemode_cog: %s", e)


def main():
    try:
        load_cogs()
    except Exception as e:
        logger.error("Failed to load extensions, starting in safe mode.")
        error_logger.error("Failed to load extensions: %s", e, exc_info=True)
        load_safe_mode()

    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
