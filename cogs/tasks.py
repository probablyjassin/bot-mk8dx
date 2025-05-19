import os
import time
import random
import json

import requests
from datetime import datetime, timezone, time, timedelta

from discord import Activity, ActivityType, Status
from discord.ext import commands, tasks

from utils.data.data_manager import data_manager, archive_type
from utils.data.state import state_manager
from utils.data.mogi_manager import mogi_manager

from utils.command_helpers.update_server_passwords import fetch_server_passwords

from config import HEALTHCHECK_URL, PASSWORD_API_URL, PASSWORD_API_PASS, LOG_CHANNEL_ID


class tasks(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if HEALTHCHECK_URL:
            self.ping_healthcheck.start()
        if PASSWORD_API_URL and PASSWORD_API_PASS:
            self.get_updated_passwords.start()

        self.change_activity.start()
        self.manage_state.start()
        self.daily_db_backup.start()

    @tasks.loop(seconds=60)
    async def ping_healthcheck(self):
        requests.get(HEALTHCHECK_URL)

    @tasks.loop(seconds=15)
    async def change_activity(self):
        status = Status.online
        for mogi in mogi_manager.read_registry().values():
            if mogi.isPlaying:
                status = Status.do_not_disturb
        activities = [
            Activity(type=ActivityType.listening, name="DK Summit OST"),
            Activity(type=ActivityType.listening, name="Mario Kart 8 Menu Music"),
            Activity(type=ActivityType.playing, name="Mario Kart Wii"),
            Activity(type=ActivityType.playing, name="Retro Rewind"),
            Activity(type=ActivityType.playing, name="on Wii Rainbow Road"),
            Activity(type=ActivityType.playing, name="Mario Kart World"),
            Activity(type=ActivityType.watching, name="Shroomless tutorials"),
            Activity(type=ActivityType.watching, name="DK Summit gapcut tutorials"),
        ]
        await self.bot.change_presence(
            status=status, activity=random.choice(activities)
        )

    @tasks.loop(seconds=5)
    async def manage_state(self):
        state_manager.backup()

    @tasks.loop(
        time=time(
            hour=22,
            minute=0,
            second=0,
            tzinfo=timezone(timedelta(hours=2), name="Europe/Berlin"),
        )
    )
    async def daily_db_backup(self):
        backup_folder = "backups"
        date_format = "%d-%m-%Y"

        os.makedirs(backup_folder, exist_ok=True)

        # Create the backup file
        backup_filename = os.path.join(
            backup_folder, f"backup_{datetime.now().strftime(date_format)}.json"
        )
        backup_data = {
            "players": data_manager.get_all_player_entries(
                archive=archive_type.INCLUDE, with_id=False
            ),
            "mogis": data_manager.get_all_mogi_entries(with_id=False),
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

        try:
            log_channel = await self.bot.fetch_channel(LOG_CHANNEL_ID)
            await log_channel.send(
                f"💾 Database backup saved to {backup_filename.split('/')[-1]}"
            )
        except Exception as e:
            print(f"Error sending database backup log: {e}")

    @tasks.loop(
        time=time(
            hour=7,
            minute=30,
            second=0,
            tzinfo=timezone(timedelta(hours=2), name="Europe/Berlin"),
        )
    )
    async def get_updated_passwords(self):
        await fetch_server_passwords(self.bot)


def setup(bot: commands.Bot):
    bot.add_cog(tasks(bot))
