from discord import SlashCommandGroup, Option, Attachment
from discord.ext import commands

from models import MogiApplicationContext

from utils.decorators import is_admin


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
            return await ctx.respond("No attachment found")

        # Prefer content_type when available, fallback to filename extension
        content_type: str = getattr(screenshot, "content_type", None)
        filename: str = (getattr(screenshot, "filename", "") or "").lower()

        is_image = False
        if content_type:
            is_image = content_type.startswith("image/")
        else:
            is_image = filename.endswith(
                (
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".webp",
                )
            )

        if not is_image:
            return await ctx.respond("Attachment is not an image")

        file = await screenshot.to_file()

        # ----- table reader magic goes here -----
        names = [
            "Edgardo",
            "KaramTNC",
            "JimDeck",
            "MITSIKU",
            "NotNiall",
            "JuulsPoms",
            "ShadowStarX",
            "jenn",
            "cars",
            "jassin",
        ]
        scores = ["12", "2", "7", "8", "3", "5", "4", "10", "6", "1"]
        # ----------------------------------------

        def ocr_to_tablestring(names: list[str], scores: list[str]) -> str:
            tablestring = "-"
            return tablestring

        await ctx.respond(file=file)


def setup(bot: commands.Bot):
    bot.add_cog(table_read(bot))
