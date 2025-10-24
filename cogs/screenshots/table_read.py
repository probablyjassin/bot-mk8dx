from discord import SlashCommandGroup, Option, Attachment
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext

from utils.decorators.checks import (
    is_admin,
)


class table_read(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    table = SlashCommandGroup(name="table", description="WIP")

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
