"""
Contains configuration settings for the Lounge Bot,
sourced from environment variables and configuration files.
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

ROOMS_CONFIG = []
FORMATS = []
FLAGS = {}

try:
    with open("lounge.config", encoding="utf-8") as f:
        data: dict = json.load(f)
        ROOMS_CONFIG: list[dict] = data["rooms"]
        FORMATS: list[str] = data["formats"]
        FLAGS: dict[str, bool] = data["debug_feature_flags"]
except (json.JSONDecodeError, FileNotFoundError) as e:
    print(f"Errors loading lounge.config: {e}")
    sys.exit(1)


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

HEALTHCHECK_URL = os.getenv("HEALTHCHECK_URL")

MONGO_URI = os.getenv("MONGO_URI")
LOUNGE_DB = os.getenv("LOUNGE_DB")

GUILD_IDS = [int(guild_id) for guild_id in os.getenv("GUILD_IDS").split(",")]

LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
MOGI_MANAGER_CHANNEL_ID = int(os.getenv("MOGI_MANAGER_CHANNEL_ID"))
RESULTS_CHANNEL_ID = int(os.getenv("RESULTS_CHANNEL_ID"))
REGISTER_CHANNEL_ID = int(os.getenv("REGISTER_CHANNEL_ID"))

YUZU_API_URL = os.getenv("YUZU_API_URL")
YUZU_SERVER_IP = os.getenv("YUZU_SERVER_IP")
SERVER_MAIN_PORT = int(os.getenv("SERVER_MAIN_PORT"))
SERVER_LOUNGE_PORT = int(os.getenv("SERVER_LOUNGE_PORT"))

PASSWORD_API_URL = os.getenv("PASSWORD_API_URL")
PASSWORD_API_PASS = os.getenv("PASSWORD_API_PASS")
