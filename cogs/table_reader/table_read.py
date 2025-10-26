from discord import SlashCommandGroup, Option, Attachment
from discord.ext import commands

from models import MogiApplicationContext
from utils.decorators import is_admin

from fuzzywuzzy import fuzz, process


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
        debug_str = ""

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

        debug_str += f"Submitted filename: {screenshot.filename}\n"

        file = await screenshot.to_file()

        # ----- table reader magic goes here -----
        names = [
            "MINITSIKU",
            "ShadowStarX",
            "jen",
            "kevin",
            "jässin8dx",
        ]
        scores = ["12", "2", "7", "8", "3"]
        # ----------------------------------------

        # if there is a mogi, try to match the names to the output
        if ctx.mogi and len(ctx.mogi.players) == len(names):
            debug_str += f"Tried to match screenshot names to lounge names\n"
            actual_names = names[:]
            choices = [player.name for player in ctx.mogi.players]

            print("thingy matching results:")
            for i, name in enumerate(names):
                match_result: tuple[str, int] | None = process.extractOne(name, choices)
                print(match_result)
                if match_result is None:
                    continue
                candidate_name, certainty = match_result

                if certainty > 70:
                    actual_names[i] = candidate_name

            names = actual_names

        def ocr_to_tablestring(names: list[str], scores: list[str]) -> str:
            tablestring = "-\n"
            for i, name in enumerate(names):
                tablestring += f"{name} {scores[i]}+\n\n"
            return tablestring

        await ctx.respond(
            f"```\n{ocr_to_tablestring(names, scores)}```\n\nDebug:{debug_str}"
        )


def setup(bot: commands.Bot):
    bot.add_cog(table_read(bot))
