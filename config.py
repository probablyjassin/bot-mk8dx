import os, json
from dotenv import load_dotenv

load_dotenv()

if not os.path.exists(".env"):
    print("Error: '.env' file does not exist. Exiting...")
    exit(1)
if not os.path.exists("room.config.json"):
    print("Error: 'room.config.json' file does not exist. Exiting...")
    exit(1)

ROOMS = []
with open("room.config.json") as f:
    ROOMS = json.load(f)


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

HEALTHCHECK_URL = os.getenv("HEALTHCHECK_URL")

MONGO_URI = os.getenv("MONGO_URI")
LOUNGE_DB = os.getenv("LOUNGE_DB")

GUILD_IDS = [int(guild_id) for guild_id in os.getenv("GUILD_IDS").split(",")]

LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
RESULTS_CHANNEL_ID = int(os.getenv("RESULTS_CHANNEL_ID"))
REGISTER_CHANNEL_ID = int(os.getenv("REGISTER_CHANNEL_ID"))

YUZU_API_URL = os.getenv("YUZU_API_URL")
YUZU_SERVER_IP = os.getenv("YUZU_SERVER_IP")
SERVER_MAIN_PORT = int(os.getenv("SERVER_MAIN_PORT"))
SERVER_LOUNGE_PORT = int(os.getenv("SERVER_LOUNGE_PORT"))
