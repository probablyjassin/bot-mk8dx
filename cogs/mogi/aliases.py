from discord import Option, slash_command
from discord.ext import commands

from models import MogiApplicationContext
from utils.decorators import with_player

from config import player_name_aliases


class aliases(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @slash_command(
        name="alias",
        description="Set the alternative in game name you're using for this mogi",
    )
    @with_player(assert_in_mogi=True)
    async def alias(
        self, ctx: MogiApplicationContext, name: str = Option(str, required=True)
    ):
        player_name_aliases[ctx.player.name] = name


def setup(bot: commands.Bot) -> None:
    bot.add_cog(aliases(bot))
