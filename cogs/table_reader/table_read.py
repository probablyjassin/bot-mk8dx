from io import BytesIO, BufferedReader

from discord import (
    SlashCommandGroup,
    message_command,
    Message,
    Option,
    Attachment,
)
from discord.ext import commands

from models import MogiApplicationContext
from utils.data import table_read_ocr_api, OCRPlayerList, store
from utils.decorators import is_admin

from fuzzywuzzy import process


def is_image(attachment: Attachment) -> bool:
    # Prefer content_type when available, fallback to filename extension
    content_type: str = getattr(attachment, "content_type", None)
    filename: str = (getattr(attachment, "filename", "") or "").lower()

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
    return is_image


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
        await ctx.defer()

        debug_str = ""

        if screenshot is None:
            return await ctx.respond("No attachment found")

        if not is_image(screenshot):
            return await ctx.respond("Attachment is not an image")

        debug_str += f"Submitted filename: {screenshot.filename}\n"

        data = await screenshot.read()

        buffer_image = BufferedReader(BytesIO(data))
        output = table_read_ocr_api(buffer_image)
        names = [entry["name"] for entry in output]
        scores = [entry["score"] for entry in output]

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
                candidate_name, _ = match_result
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

    @message_command(
        name="Tablestring->Add points from Img",
    )
    @is_admin()
    async def add(self, ctx: MogiApplicationContext, message: Message):
        await ctx.defer()

        record = await store.get_bytes(ctx.guild_id, ctx.author.id)
        if not record:
            await ctx.respond(
                "You haven't selected an image yet (or it expired). Right-click a message → Apps → Select Image.",
                ephemeral=True,
            )
            return

        if len(message.attachments):
            return await ctx.respond(
                "The message you selected has attachments. \nThis command is for the **tablestring** *after* you used 'Select Image' on the screenshot.",
                ephemeral=True,
            )

        output = table_read_ocr_api(BufferedReader(BytesIO(record)))
        names = [int(entry["name"]) for entry in output]
        scores = [int(entry["score"]) for entry in output]

        tablestring = message.content
        players: list[str] = []
        points: list[int] = []
        for line in tablestring.splitlines():
            if line.strip(" |+") and len(line.split()) == 2:
                players.append(line.split()[0])
                points.append(eval(line.split()[1].replace("|", "+").strip(" |+")))

        return await ctx.respond(
            f"OCR from image: {names}|{scores}\ntablestring: {players}{points}"
        )


def setup(bot: commands.Bot):
    bot.add_cog(table_read(bot))
