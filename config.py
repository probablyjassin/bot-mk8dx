import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')
LOUNGE_DB = os.getenv('LOUNGE_DB')
GUILD_IDS = [int(guild_id) for guild_id in os.getenv('GUILD_IDS').split(',')]
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID'))
REGISTER_CHANNEL_ID = int(os.getenv('REGISTER_CHANNEL_ID'))
