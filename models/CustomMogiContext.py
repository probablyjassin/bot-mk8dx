import discord
from discord.utils import get

from utils.data.mogi_manager import mogi_manager
from models.MogiModel import Mogi

from config import GUILD_IDS, RESULTS_CHANNEL_ID, REGISTER_CHANNEL_ID


class MogiApplicationContext(discord.ApplicationContext):
    """## `discord.ApplicationContext` with custom Lounge attributes:
    - `mogi`: `Mogi` object of the channel
    - `main_guild`: `discord.Guild` object of the main guild
    - `inmogi_role`: `discord.Role` object of the InMogi role
    - `get_lounge_role(name: str)`: method to get a role by name

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

        self.register_channel: discord.TextChannel = get(
            self.main_guild.text_channels, id=REGISTER_CHANNEL_ID
        )
        self.results_channel: discord.TextChannel = get(
            self.main_guild.text_channels, id=RESULTS_CHANNEL_ID
        )

    def get_lounge_role(self, name: str) -> discord.Role:
        return get(self.main_guild.roles, name=name)
