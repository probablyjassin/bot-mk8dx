import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')
LOUNGE_DB = os.getenv('LOUNGE_DB')
GUILD_ID = os.getenv('GUILD_ID')
ERROR_CHANNEL_ID = os.getenv('ERROR_CHANNEL_ID')
REGISTER_CHANNEL_ID = os.getenv('REGISTER_CHANNEL_ID')
