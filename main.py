import os
import discord
from discord.ext import commands
from config import DISCORD_TOKEN
from logger import setup_logger, normal, highlight

logger = setup_logger(__name__)

intents = discord.Intents.all()

owners = [769525682039947314, 450728788570013721]

class customBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    async def close(self):
        for name,cog in self.cogs.items():
            cog._eject(self)
            print(f"Ejected {name}")
        await super().close()

bot = customBot(
    command_prefix=".", case_insensitive = True, help_command = None,
    intents=intents, owner_ids = set(owners), 
    status=discord.Status.online, activity=discord.Streaming(name="ones and zeroes", url="https://www.youtube.com/watch?v=xvFZjo5PgG0")
)

@bot.event
async def on_ready():
    logger.info(f'Logged into Discord')
    print(f"""
        {highlight(bot.user)}
        ID: {highlight(bot.user.id)}
    """)
    
    logger.debug("Guilds:")
    for guild in bot.guilds:
        print(guild.name)
    logger.debug("--------")

def load_extensions():
    logger.debug("----Loading extensions----")
    for root, dirs, files in os.walk('./cogs'):
        for file in files:
            if file.endswith('.py'):
                cog_path = os.path.join(root, file)
                extension = cog_path[2:].replace('/', '.').replace('\\', '.').replace('.py', '')
                bot.load_extension(extension)
                print(f"Loaded {normal(extension)}")
    logger.debug("----Finished loading extensions----")

def main():
    load_extensions()
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()
