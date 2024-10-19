import os
import discord
from discord.ext import commands

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
    print(f'Logged into Discord as {bot.user.name} | ID: {bot.user.id}')
    print("Guilds:")
    for guild in bot.guilds:
        print(guild.name)
    print("--------")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

for filename in os.listdir('./cogs/mogi'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.mogi.{filename[:-3]}')

bot.run(os.getenv('DISCORD_TOKEN'))