import discord
from discord.utils import get

from utils.data.mogi_manager import mogi_manager
from models.MogiModel import Mogi

from config import GUILD_IDS


class MogiApplicationContext(discord.ApplicationContext):
    """## `discord.ApplicationContext` but with the `mogi` attribute:

    Represents a Discord application command interaction context.

    This class is not created manually and is instead passed to application
    commands as the first parameter.

    .. versionadded:: 2.0

    Attributes
    ----------
    bot: :class:`.Bot`
        The bot that the command belongs to.
    interaction: :class:`.Interaction`
        The interaction object that invoked the command.
    command: :class:`.ApplicationCommand`
        The command that this context belongs to.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mogi: Mogi = mogi_manager.get_mogi(self.channel.id)

        self.main_guild: discord.Guild = get(self.bot.guilds, id=GUILD_IDS[0])
        self.inmogi_role: discord.Role = get(self.main_guild.roles, name="InMogi")

    def get_lounge_role(self, name: str) -> discord.Role:
        return get(self.main_guild.roles, name=name)
