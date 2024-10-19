import random

import discord
from discord.ext import commands, tasks

class tasks(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
      
    @commands.Cog.listener()
    async def on_ready(self):
        self.change_activity.start()

    @tasks.loop(seconds=15)
    async def change_activity(self):
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
        await self.bot.change_presence(activity = random.choice(activities))

def setup(bot: commands.Bot):
    bot.add_cog(tasks(bot))
