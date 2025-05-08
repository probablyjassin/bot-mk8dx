import os
import time
import random
import json

import requests
from datetime import datetime, timezone, time, timedelta

from discord import Activity, ActivityType, Streaming
from discord.ext import commands, tasks

from utils.data.state import state_manager
from utils.data.database import db_players, db_mogis

from config import HEALTHCHECK_URL


class tasks(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if HEALTHCHECK_URL:
            self.ping_healthcheck.start()

        self.change_activity.start()
        self.manage_state.start()
        self.daily_db_backup.start()

    @tasks.loop(seconds=60)
    async def ping_healthcheck(self):
        requests.get(HEALTHCHECK_URL)

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
        ]
        await self.bot.change_presence(activity=random.choice(activities))

    @tasks.loop(seconds=5)
    async def manage_state(self):
        state_manager.backup()

    @tasks.loop(time=time(hour=22, minute=0, second=0, tzinfo=timezone.utc))
    async def daily_db_backup(self):
        backup_folder = "backups"
        date_format = "%d-%m-%Y"

        os.makedirs(backup_folder, exist_ok=True)

        # Create the backup file
        backup_filename = os.path.join(
            backup_folder, f"backup_{datetime.now().strftime(date_format)}.json"
        )
        backup_data = {
            "players": list(db_players.find({}, {"_id": 0})),
            "mogis": list(db_mogis.find({}, {"_id": 0})),
        }

        with open(backup_filename, "w") as backup_file:
            json.dump(backup_data, backup_file, indent=4)

        # Remove backups older than 3 days
        for filename in os.listdir(backup_folder):
            file_path = os.path.join(backup_folder, filename)
            if os.path.isfile(file_path):
                file_date_str = filename.split("_")[1].split(".")[0]
                file_date = datetime.strptime(file_date_str, date_format)
                if datetime.now() - file_date > timedelta(days=3):
                    os.remove(file_path)


def setup(bot: commands.Bot):
    bot.add_cog(tasks(bot))
