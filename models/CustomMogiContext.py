from discord import ApplicationContext, Member, Guild, Role, TextChannel
from discord.utils import get

from utils.data import mogi_manager, data_manager
from .MogiModel import Mogi
from .PlayerModel import PlayerProfile
from .GuildModel import Guild

from config import GUILD_IDS, RESULTS_CHANNEL_ID, REGISTER_CHANNEL_ID


class MogiApplicationContext(ApplicationContext):
    """## `discord.ApplicationContext` with custom Lounge attributes:
    - `mogi`: `Mogi` object of the channel
    - `player`: `PlayerProfile` object passed down by the `@with_player` decorator, `None` if not used
    - `player_discord`: `Member` object passed down by the `@with_player` decorator, `None` if not used
    - `lounge_guild`: `Guild` The guild the player is in (if applicable)
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

        self.mogi: Mogi | None = mogi_manager.get_mogi(self.channel.id)
        self.player: PlayerProfile | None = None
        self.player_discord: Member | None = None

        self.lounge_guild: Guild | None = None

        self.main_guild: Guild = get(self.bot.guilds, id=GUILD_IDS[0])
        self.inmogi_role: Role = get(self.main_guild.roles, name="InMogi")

        self.register_channel: TextChannel = get(
            self.main_guild.text_channels, id=REGISTER_CHANNEL_ID
        )
        self.results_channel: TextChannel = get(
            self.main_guild.text_channels, id=RESULTS_CHANNEL_ID
        )

    def get_lounge_role(self, name: str) -> Role:
        return get(self.main_guild.roles, name=name)
