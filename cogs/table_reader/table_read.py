import re
from io import BytesIO, BufferedReader
from aiohttp import ClientResponseError
from typing import Optional

from discord import (
    SlashCommandGroup,
    message_command,
    Message,
    Option,
    Attachment,
)
from discord.ext import commands

from models import PlayerProfile, MogiApplicationContext, RestrictedOption
from utils.data import (
    table_read_ocr_api,
    pattern_match_lounge_names,
    ocr_to_tablestring,
    group_tablestring_by_teams,
    store,
)
from utils.command_helpers import player_name_autocomplete
from utils.decorators import is_mogi_manager, with_player
from utils.decorators.checks import LoungeRole

from services.players import find_player_profile
from services.miscellaneous import set_player_alias, get_all_aliases

MSG_WARN = "⚠️ The scores don't fully add up! Double check them for errors."
MSG_CORRECT = "✅ The scores seem to fully add up. Still double check with Lorenzi!"

scoring_regex = r"^ \+?(?:\d+\+)*\d+\s*"


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


async def image_data_to_tablestring(
    buffer_image: BufferedReader,
    mogi_teams: Optional[list[list[PlayerProfile]]] = None,
    mogi_format: Optional[int] = None,
    team_tags: Optional[list[str]] = None,
) -> tuple[str, bool]:

    output, warnings = await table_read_ocr_api(buffer_image)

    ocr_names = [entry["name"] for entry in output]
    scores = [entry["score"] for entry in output]

    # if there is a mogi, try to match the names to the output
    mogi_players = []
    if mogi_teams:
        mogi_players = [player for team in mogi_teams for player in team]

    if mogi_players:
        potential_actual_names = await pattern_match_lounge_names(
            ocr_names, [player.name for player in mogi_players]
        )
        if potential_actual_names:
            ocr_names.clear()
            for name in potential_actual_names:
                ocr_names.append(name)

    created_tablestring = ocr_to_tablestring(ocr_names, scores)

    if mogi_format and mogi_format >= 2:

        if potential_grouped_tablestring := group_tablestring_by_teams(
            tablestring=created_tablestring,
            teams=mogi_teams,
            team_tags=team_tags,
        ):
            created_tablestring = potential_grouped_tablestring

    return created_tablestring, bool(warnings)


class table_read(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    table = SlashCommandGroup(name="table", description="WIP")

    @table.command(
        name="read",
        description="Get a tablestring from a screenshot",
    )
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

        if screenshot is None:
            return await ctx.respond("No attachment found")

        if not is_image(screenshot):
            return await ctx.respond("Attachment is not an image")

        data = await screenshot.read()

        buffer_image = BufferedReader(BytesIO(data))

        created_tablestring = None

        try:
            created_tablestring, has_warns = await image_data_to_tablestring(
                buffer_image=buffer_image,
                mogi_teams=ctx.mogi.teams if ctx.mogi else None,
                mogi_format=ctx.mogi.format if ctx.mogi else None,
                team_tags=ctx.mogi.team_tags if ctx.mogi else None,
            )
        except ClientResponseError as e:
            return await ctx.respond(
                f"Table reader API returned an error: HTTP {e.status} - {e.message}"
            )
        except Exception as e:
            return await ctx.respond(f"Error reading table: {str(e)}")

        await ctx.respond(
            f"```\n{created_tablestring}```"
            + "\n"
            + (MSG_WARN if has_warns else MSG_CORRECT)
        )

    @message_command(
        name="Read Table",
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

        if screenshot is None:
            return await ctx.respond("No attachment found")

        data = await screenshot.read()

        buffer_image = BufferedReader(BytesIO(data))

        created_tablestring = None

        try:
            created_tablestring, has_warns = await image_data_to_tablestring(
                buffer_image=buffer_image,
                mogi_teams=ctx.mogi.teams if ctx.mogi else None,
                mogi_format=ctx.mogi.format if ctx.mogi else None,
                team_tags=ctx.mogi.team_tags if ctx.mogi else None,
            )

        except ClientResponseError as e:
            return await ctx.respond(
                f"Table reader API returned an error: HTTP {e.status} - {e.message}"
            )
        except Exception as e:
            return await ctx.respond(f"Error reading table: {str(e)}")

        await ctx.respond(
            f"```\n{created_tablestring}```"
            + "\n"
            + (MSG_WARN if has_warns else MSG_CORRECT)
        )

    @message_command(
        name="Tablestring->Add points from Img",
    )
    async def add(self, ctx: MogiApplicationContext, message: Message):
        await ctx.defer()

        divider: str = "|" if "|" in message.content else "+"

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

        try:
            output, warnings = await table_read_ocr_api(BufferedReader(BytesIO(record)))
        except ClientResponseError as e:
            return await ctx.respond(
                f"Error reading table: HTTP {e.status} - {e.message}"
            )
        except Exception as e:
            return await ctx.respond(f"Error reading table: {str(e)}")

        ocr_names = [entry["name"] for entry in output]
        scores = [entry["score"] for entry in output]

        # Extract player names from tablestring (use original content before divider replacement)
        players: list[str] = []
        for line in message.content.splitlines():
            line = line.strip()
            # Skip empty lines and team headers (lines without scores)
            if not line or not re.search(scoring_regex, line):
                continue
            # Extract name by removing all trailing score patterns
            name = re.sub(scoring_regex, "", line).strip()
            if name:
                players.append(name)

        # if there is a mogi, try to match the names to the output
        potential_actual_names = []

        # Now apply divider replacement for processing
        divider: str = "|" if "|" in message.content else "+"
        tablestring = message.content.replace("|", divider).replace("+", divider)

        if ctx.mogi and len(ctx.mogi.players) == len(ocr_names):
            potential_actual_names = await pattern_match_lounge_names(
                ocr_names, [player.name for player in ctx.mogi.players]
            )
            if potential_actual_names:
                if set(players) == set(potential_actual_names):
                    ocr_names = potential_actual_names
                else:
                    return await ctx.respond(
                        f"Matched lounge names but they don't fit with the selected tablestring:\n"
                        f"Detected Names: `{ocr_names}`\n"
                        f"Matched Lounge Names: `{potential_actual_names}`\n"
                        f"Names on tablestring: `{players}`"
                    )
            else:
                return await ctx.respond(
                    "Could not match lounge names to in-game names"
                )

        # Build lookup dictionary for scores
        score_lookup = {}
        for name, score in zip(ocr_names, scores):
            score_lookup[name.strip().lower()] = str(score)

        new_lines = []
        for line in tablestring.splitlines():
            stripped_line = line.strip()

            # Check if this line has a player score (ends with number+optional plus)
            if stripped_line and re.search(scoring_regex, stripped_line):
                # Extract the player name
                name = re.sub(scoring_regex, "", stripped_line).strip()

                # Look up the OCR score
                name_key = name.strip().lower()
                if name_key in score_lookup:
                    # Ensure line ends with divider
                    if not line.rstrip().endswith(divider):
                        line = line.rstrip() + divider
                    line = line.rstrip() + score_lookup[name_key]
                else:
                    return await ctx.respond(
                        f"Couldn't find player '{name}' in OCR results.\n"
                        f"OCR Names: `{ocr_names}`\n"
                        f"Tablestring Names: `{players}`"
                    )

            new_lines.append(line)

        updated_tablestring = "\n".join(new_lines)
        return await ctx.respond(
            f"```\n{updated_tablestring}\n```\n"
            + (MSG_WARN if warnings else MSG_CORRECT)
        )

    @table.command(
        name="alias",
        description="Set the alternative in game name you're using for this mogi",
    )
    @with_player(assert_in_mogi=True)
    async def alias(
        self,
        ctx: MogiApplicationContext,
        name: str = Option(str, required=True),
        to_player: str = RestrictedOption(
            str,
            required=False,
            autocomplete=player_name_autocomplete,
            required_role=LoungeRole.MOGI_MANAGER,
        ),
    ):
        searched_player = (
            await find_player_profile(query=to_player) if to_player else None
        )
        if to_player and not searched_player:
            return await ctx.respond("Couldn't find that player")

        await set_player_alias(searched_player if searched_player else ctx.player, name)
        return await ctx.respond(
            f"{searched_player.name if searched_player else ctx.player.name} -> `{name}`"
        )

    @table.command(name="list_aliases")
    async def list_aliases(self, ctx: MogiApplicationContext):
        await ctx.respond(
            "\n".join(
                f"{key}: {value}"
                for key, value in (await get_all_aliases()).items()
                if key != "_id"
            )
        )


def setup(bot: commands.Bot):
    bot.add_cog(table_read(bot))
