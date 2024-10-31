import discord
from utils.data.mogi_manager import mogi_manager


class MogiApplicationContext(discord.ApplicationContext):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mogi = mogi_manager.get_mogi(self.channel.id)
