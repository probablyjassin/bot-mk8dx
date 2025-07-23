from discord import slash_command, Option, Attachment
from discord.ext import commands
from pycord.multicog import subcommand

from models.CustomMogiContext import MogiApplicationContext

from utils.decorators.checks import (
    is_mogi_in_progress,
    is_mogi_manager,
)


class screenshots(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @subcommand(group="points")
    @slash_command(name="ss", description="Collect a screenshot (during mogi)")
    @is_mogi_manager()
    @is_mogi_in_progress()
    async def ss(
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

        # Store the screenshot (you can modify this logic as needed)
        if not hasattr(ctx.mogi, "screenshots"):
            ctx.mogi.screenshots = []

        ctx.mogi.screenshots.append(
            {"url": image.url, "filename": image.filename, "user": ctx.author.id}
        )

        await ctx.respond(f"Screenshot `{image.filename}` has been collected.")


def setup(bot: commands.Bot):
    bot.add_cog(screenshots(bot))
