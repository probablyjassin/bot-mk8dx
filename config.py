"""
Contains configuration settings for the Lounge Bot,
sourced from environment variables and configuration files.
"""

import os
import sys
import json
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()


class LoungeBotConfig(TypedDict):
    # lounge
    season: int
    formats: list

    # discord
    guilds: list[str]
    logchannelid: str
    registerchannelid: str
    resultschannelid: str
    mogimanagerchannelid: str

    # yuzu servers
    yuzu_api_url: str
    yuzu_server_ip: str
    yuzu_port_main: int
    yuzu_port_lounge: int

    rooms: list[dict[str, str | int]]

    password_api_url: int

    table_reader_url: str


def load_config_file(filepath: str, required_keys: list[str]) -> dict:
    """Load and parse a JSON config file."""
    filepath = f"config/{filepath}"

    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

    except FileNotFoundError:
        print(f"Error: Config file not found: {filepath}")
        sys.exit(1)

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}")
        sys.exit(1)

    # Check for required variables
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        print(
            f"Error: Missing required key(s) in {filepath}: {', '.join(missing_keys)}"
        )
        sys.exit(1)

    return data


lounge: LoungeBotConfig = load_config_file("lounge.config", ["season", "formats"])

discord: LoungeBotConfig = load_config_file(
    "discord.config",
    [
        "guilds",
        "logchannelid",
        "registerchannelid",
        "resultschannelid",
        "mogimanagerchannelid",
    ],
)

yuzu: LoungeBotConfig = load_config_file(
    "yuzu.config",
    [
        "yuzu_api_url",
        "yuzu_server_ip",
        "yuzu_port_main",
        "yuzu_port_lounge",
        "rooms",
        "password_api_url",
        "table_reader_url",
    ],
)


# lounge config
SEASON = lounge["season"]
FORMATS = lounge["formats"]

# discord
GUILD_IDS = [int(discord_id) for discord_id in discord["guilds"]]
LOG_CHANNEL_ID = int(discord["logchannelid"])
REGISTER_CHANNEL_ID = int(discord["registerchannelid"])
RESULTS_CHANNEL_ID = int(discord["resultschannelid"])
MOGI_MANAGER_CHANNEL_ID = int(discord["mogimanagerchannelid"])

# yuzu
YUZU_API_URL = yuzu["yuzu_api_url"]
YUZU_SERVER_IP = yuzu["yuzu_server_ip"]
SERVER_MAIN_PORT = yuzu["yuzu_port_main"]
SERVER_LOUNGE_PORT = yuzu["yuzu_port_lounge"]

ROOMS_CONFIG = yuzu["rooms"]

PASSWORD_API_URL = yuzu["password_api_url"]
TABLE_READER_URL = yuzu["table_reader_url"]

# environment variables
DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN")

MONGO_URI: str = os.getenv("MONGO_URI")
LOUNGE_DB: str = os.getenv("LOUNGE_DB")

PASSWORD_API_PASS: str = os.getenv("PASSWORD_API_PASS")
HEALTHCHECK_URL: str = os.getenv("HEALTHCHECK_URL")
