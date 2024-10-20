import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')
LOUNGE_DB = os.getenv('LOUNGE_DB')
ERROR_CHANNEL = os.getenv('ERROR_CHANNEL')