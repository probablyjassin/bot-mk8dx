import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')