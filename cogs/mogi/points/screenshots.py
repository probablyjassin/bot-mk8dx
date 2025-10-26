import aiohttp
from pathlib import Path
from discord import slash_command, Option, Attachment, File, SlashCommandGroup
from discord.ext import commands
from pycord.multicog import subcommand

from models import MogiApplicationContext

from utils.decorators.checks import (
    is_mogi_in_progress,
    is_mogi_manager,
)


class screenshots(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    ss = SlashCommandGroup("ss", "Screenshot management commands")

    @ss.command(name="save", description="Save a screenshot (during mogi)")
    @is_mogi_manager()
    @is_mogi_in_progress()
    async def save(
        self,
        ctx: MogiApplicationContext,
        image: Attachment = Option(Attachment, "paste the screenshot"),
        races: int = Option(
            int,
            "How many races are IN THIS SCREENSHOT?",
        ),
        total: int = Option(int, "How many races have you PLAYED (TOTAL) so far?"),
    ):
        await ctx.response.defer()

        if not image.content_type or not image.content_type.startswith("image/"):
            return await ctx.respond("Please provide a valid image file.")

        # Create directory structure: state/screenshots/{channel_id}/
        screenshots_dir = Path("state") / "screenshots" / str(ctx.channel.id)
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Create new filename with race information
        new_filename = f"races_{races}_total_{total}_{image.filename}"
        file_path = screenshots_dir / new_filename

        try:
            # Download and save the image
            async with aiohttp.ClientSession() as session:
                async with session.get(image.url) as response:
                    if response.status == 200:
                        with open(file_path, "wb") as f:
                            f.write(await response.read())
                    else:
                        return await ctx.respond("Failed to download the image.")

            await ctx.respond(
                f"Screenshot `{image.filename}` has been saved as `{new_filename}`"
            )

        except Exception as e:
            await ctx.respond(f"Error saving screenshot: {str(e)}")


def setup(bot: commands.Bot):
    bot.add_cog(screenshots(bot))
