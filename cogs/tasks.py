import random

from discord import Activity, ActivityType, Streaming
from discord.ext import commands, tasks

from utils.data.state import state_manager


class tasks(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.change_activity.start()
        self.manage_state.start()

    @tasks.loop(seconds=15)
    async def change_activity(self):
        activities = [
            Activity(type=ActivityType.listening, name="DK Summit OST"),
            Activity(type=ActivityType.listening, name="Mario Kart 8 Menu Music"),
            Activity(type=ActivityType.playing, name="Mario Kart Wii"),
            Activity(type=ActivityType.playing, name="Retro Rewind"),
            Activity(type=ActivityType.playing, name="on Wii Rainbow Road"),
            Activity(type=ActivityType.watching, name="Shroomless tutorials"),
            Activity(type=ActivityType.watching, name="DK Summit gapcut tutorials"),
            Streaming(
                name="ones and zeroes",
                url="https://www.youtube.com/watch?v=xvFZjo5PgG0&autoplay=1",
            ),
        ]
        await self.bot.change_presence(activity=random.choice(activities))

    @tasks.loop(seconds=5)
    async def manage_state(self):
        state_manager.backup()


def setup(bot: commands.Bot):
    bot.add_cog(tasks(bot))
