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
from utils.data import data_manager
from utils.command_helpers import player_name_autocomplete
from utils.decorators import is_mogi_manager, with_player
from utils.decorators.checks import _is_at_least_role, LoungeRole


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
) -> str:
    mogi_players = [player for team in mogi_teams for player in team]

    output = await table_read_ocr_api(buffer_image)

    ocr_names = [entry["name"] for entry in output]
    scores = [entry["score"] for entry in output]

    # if there is a mogi, try to match the names to the output
    if mogi_players and len(mogi_players) == len(ocr_names):
        potential_actual_names = await pattern_match_lounge_names(
            ocr_names, [player.name for player in mogi_players]
        )
        if potential_actual_names:
            ocr_names = potential_actual_names

    created_tablestring = ocr_to_tablestring(ocr_names, scores)

    if mogi_format and mogi_format >= 2:

        if potential_grouped_tablestring := group_tablestring_by_teams(
            tablestring=created_tablestring,
            teams=mogi_teams,
            team_tags=team_tags,
        ):
            created_tablestring = potential_grouped_tablestring

    return created_tablestring


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

        if screenshot is None:
            return await ctx.respond("No attachment found")

        if not is_image(screenshot):
            return await ctx.respond("Attachment is not an image")

        data = await screenshot.read()

        buffer_image = BufferedReader(BytesIO(data))

        created_tablestring = None

        try:
            created_tablestring = await image_data_to_tablestring(
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

        await ctx.respond(f"```\n{created_tablestring}```")

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
            created_tablestring = await image_data_to_tablestring(
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

        await ctx.respond(f"```\n{created_tablestring}```")

    @message_command(
        name="Tablestring->Add points from Img",
    )
    @is_mogi_manager()
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

        tablestring = message.content.replace("|", divider).replace("+", divider)

        try:
            output = await table_read_ocr_api(BufferedReader(BytesIO(record)))
        except ClientResponseError as e:
            return await ctx.respond(
                f"Error reading table: HTTP {e.status} - {e.message}"
            )
        except Exception as e:
            return await ctx.respond(f"Error reading table: {str(e)}")

        names = [entry["name"] for entry in output]
        scores = [entry["score"] for entry in output]

        players: list[str] = []
        for line in tablestring.splitlines():
            if line.strip(" |+") and len(line.split()) == 2:
                name = re.sub(r"\s+[\d|+]+\s*$", "", line).strip()
                if name:
                    players.append(name)
                else:
                    return await ctx.respond(
                        "Error reading out player name from the tablestring."
                    )

        # if there is a mogi, try to match the names to the output
        if ctx.mogi and len(ctx.mogi.players) == len(names):
            potential_actual_names = await pattern_match_lounge_names(
                names, [player.name for player in ctx.mogi.players]
            )
            if potential_actual_names:
                if set(players) == set(potential_actual_names):
                    names.clear()
                    names.extend(potential_actual_names)
                else:
                    return await ctx.respond(
                        f"Matched lounge names but they don't fit with the selected tablestring:\n"
                        f"Detected Names: `{names}`\n"
                        f"Matched Lounge Names: `{potential_actual_names}`\n"
                        f"Names on tablestring: `{players}`"
                    )
            else:
                return await ctx.respond(
                    "Could not match lounge names to in-game names"
                )

        new_lines = []
        for line in tablestring.splitlines():
            print(line)
            if (
                line.strip(" |+")
                and len(line.split()) == 2
                and line.split()[1].replace(divider, "").isnumeric()
                # points.append(eval(line.split()[1].replace("|", "+").strip(" |+")))
            ):
                if not line.endswith(divider):
                    line += divider
                try:
                    line += scores[names.index(line.split()[0])]
                except:
                    return await ctx.respond(
                        f"Couldn't find {line.split()[0]}\n"
                        f"Names:\n{names}\n"
                        f"Matched Lounge Names: `{potential_actual_names}`"
                    )
            new_lines.append(line)
        return await ctx.respond("\n".join(new_lines))

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
            await data_manager.Players.find(query=to_player) if to_player else None
        )
        if to_player and not searched_player:
            return await ctx.respond("Couldn't find that player")

        await data_manager.Aliases.set_player_alias(
            searched_player if searched_player else ctx.player, name
        )
        return await ctx.respond(
            f"{searched_player.name if searched_player else ctx.player.name} -> `{name}`"
        )

    @table.command(name="list_aliases")
    async def list_aliases(self, ctx: MogiApplicationContext):
        await ctx.respond(
            "\n".join(
                f"{key}: {value}"
                for key, value in (await data_manager.Aliases.get_all_aliases()).items()
                if key != "_id"
            )
        )


def setup(bot: commands.Bot):
    bot.add_cog(table_read(bot))
