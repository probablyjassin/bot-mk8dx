from config import ROOMS_CONFIG, LOG_CHANNEL_ID

from discord import SlashCommandGroup, Option, File, Attachment
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from models.RoomModel import Room

from utils.data.data_manager import data_manager, archive_type
from utils.data.mogi_manager import mogi_manager
from utils.data.state import state_manager
from utils.command_helpers.confirm import confirmation
from utils.decorators.checks import (
    is_admin,
)


from utils.command_helpers.update_server_passwords import fetch_server_passwords


class table_read(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    table = SlashCommandGroup(name="table", description="Debugging commands")

    @table.command(
        name="read",
        description="Get a tablestring from a screenshot",
    )
    @is_admin()
    async def read(
        self,
        ctx: MogiApplicationContext,
        screenshot: Attachment = Option(
            Attachment,
            "Attachment or File",
            required=True,
        ),
    ):
        if screenshot is None:
            return await ctx.send("No attachment found")

        file = await screenshot.to_file()
        await ctx.send(file=file)


def setup(bot: commands.Bot):
    bot.add_cog(table_read(bot))
