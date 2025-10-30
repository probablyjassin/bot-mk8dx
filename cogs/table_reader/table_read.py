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
from utils.data import (
    table_read_ocr_api,
    pattern_match_lounge_names,
    ocr_to_tablestring,
    store,
)
from utils.decorators import is_mogi_manager, with_player
from config import player_name_aliases


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
    @is_mogi_manager()
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
        print("api result:")
        print(output)
        ocr_names = [entry["name"] for entry in output]
        scores = [entry["score"] for entry in output]

        # if there is a mogi, try to match the names to the output
        if ctx.mogi and len(ctx.mogi.players) == len(ocr_names):
            potential_actual_names = pattern_match_lounge_names(
                ocr_names, [player.name for player in ctx.mogi.players]
            )
            if potential_actual_names:
                ocr_names = potential_actual_names

        await ctx.respond(
            f"```\n{ocr_to_tablestring(ocr_names, scores)}```\n\nDebug:{debug_str}"
        )

    """ @message_command(
        name="Screenshot to Tablestring",
        description="Get a tablestring from a screenshot",
    )
    async def read(self, ctx: MogiApplicationContext, message: Message):
        await ctx.defer()

        screenshot: Attachment = None

        for a in message.attachments:
            if a.content_type and a.content_type.startswith("image/"):
                screenshot = a
                break
            # fallback on filename extension if content_type missing
            if any(
                a.filename.lower().endswith(ext)
                for ext in (".png", ".jpg", ".jpeg", ".gif", ".webp")
            ):
                screenshot = a
                break

        debug_str = ""

        if screenshot is None:
            return await ctx.respond("No attachment found")

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
        ) """

    @message_command(
        name="Tablestring->Add points from Img",
    )
    @is_mogi_manager()
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
        names = [entry["name"] for entry in output]
        scores = [entry["score"] for entry in output]

        await ctx.channel.send(f"Names:\n{names}\n\nScores:{scores}")

        tablestring = message.content
        players: list[str] = []
        for line in tablestring.splitlines():
            if line.strip(" |+") and len(line.split()) == 2:
                players.append(line.split()[0])

        # if there is a mogi, try to match the names to the output
        if ctx.mogi and len(ctx.mogi.players) == len(names):
            await ctx.channel.send("trying to match lounge names")
            potential_actual_names = pattern_match_lounge_names(
                names, [player.name for player in ctx.mogi.players]
            )
            if potential_actual_names:
                if set(players).issubset(set(potential_actual_names)):
                    names.clear()
                    names.extend(potential_actual_names)
                else:
                    await ctx.channel.send(
                        "matched lounge names but they don't fit with the selected tablestring"
                    )
            else:
                await ctx.channel.send("could not match lounge names")

        new_lines = []
        for line in tablestring.splitlines():
            print(line)
            if (
                line.strip(" |+")
                and len(line.split()) == 2
                and line.split()[1].replace("+", "").replace("|", "").isnumeric()
            ):
                if not line.endswith("+"):
                    line += "+"
                line += scores[names.index(line.split()[0])]
                print(line)
            new_lines.append(line)

        # points.append(eval(line.split()[1].replace("|", "+").strip(" |+")))

        return await ctx.respond("\n".join(new_lines))

    @table.command(
        name="alias",
        description="Set the alternative in game name you're using for this mogi",
    )
    @with_player(assert_in_mogi=True)
    async def alias(
        self, ctx: MogiApplicationContext, name: str = Option(str, required=True)
    ):
        player_name_aliases[ctx.player.name] = name
        return await ctx.respond(f"-> `{name}`")


def setup(bot: commands.Bot):
    bot.add_cog(table_read(bot))
