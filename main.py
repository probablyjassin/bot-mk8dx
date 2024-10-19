import os, json, discord, pymongo, random
import re
from pymongo import collection
from copy import deepcopy
from discord.ext import commands, tasks
from dotenv import load_dotenv
load_dotenv()

import cogs.extras.mogi_config as config
default_mogi_state = deepcopy(config.mogi_config)

try:
    import config as custom_config
    for key in custom_config.custom_config.keys():
        default_mogi_state[key] = custom_config.custom_config[key]
except ImportError:
    pass

intents = discord.Intents.all()

owners = [769525682039947314, 450728788570013721]

class customBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.mogi: object = default_mogi_state
        # common messages
        self.no_mogi = "Currently no mogi open"
        self.locked_mogi = "The Mogi is already running. Players can't join, leave or close it before it finished."

        return super().__init__(*args, **kwargs)
    

    async def close(self):
        for name,cog in self.cogs.items():
            cog._eject(self)
            print(f"Ejected {name}")
        self.client.close()
        await super().close()


bot = customBot(
    command_prefix=".", case_insensitive = True, help_command = None,
    intents=intents, owner_ids = set(owners), 
    status=discord.Status.online, activity=discord.Streaming(name="ones and zeroes", url="https://www.youtube.com/watch?v=xvFZjo5PgG0")
)

@tasks.loop(seconds=15)
async def change_activity():
    activities = [
        discord.Activity(type=discord.ActivityType.listening, name="DK Summit OST"),
        discord.Activity(type=discord.ActivityType.listening, name="Mario Kart 8 Menu Music"),
        discord.Activity(type=discord.ActivityType.playing, name="Mario Kart Wii"),
        discord.Activity(type=discord.ActivityType.playing, name="Retro Rewind"),
        discord.Activity(type=discord.ActivityType.playing, name="on Wii Rainbow Road"),
        discord.Activity(type=discord.ActivityType.watching, name="Shroomless tutorials"),
        discord.Activity(type=discord.ActivityType.watching, name="DK Summit gapcut tutorials"),
        discord.Streaming(name="ones and zeroes", url="https://www.youtube.com/watch?v=xvFZjo5PgG0&autoplay=1")
    ]
    await bot.change_presence(activity = random.choice(activities))

@tasks.loop(minutes=5)
async def update_lounge_pass():
    new_password = ""
    with open("persistent/password.txt", "r") as f:
        new_password = f.read()
        f.close()

    channel = bot.get_channel(1222294894962540704)
    last_message = await channel.history(limit=1).flatten()

    match = re.search(r"`([^`]+)`", last_message[0].content)
    if match:
        if new_password.strip() != match.group(1).strip():
            await channel.purge()
            await channel.send(f"# Current password: `{new_password.strip()}`\nIf the password is wrong, you might see an outdated version of this message. Restart your Discord with `Ctrl + R`\nPlease do not distribute the password in other channels, instead refer to https://discord.com/channels/1084911987626094654/1222294894962540704 \nThis message will change for future password changes!")

@tasks.loop(seconds=5)
async def backup_state():
    with open("persistent/backup.json", "w") as f:
            json.dump(bot.mogi, f)
            f.close()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    change_activity.start()
    with open("persistent/backup.json", "r") as f:
        bot.mogi = json.load(f)
        f.close()
    backup_state.start()
    update_lounge_pass.start()

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

for filename in os.listdir('./cogs/mogi'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.mogi.{filename[:-3]}')

bot.run(os.getenv('DISCORD_TOKEN'))