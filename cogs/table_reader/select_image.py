from discord import slash_command, message_command, Message, Option, Attachment, Embed
from discord.ext import commands
from pycord.multicog import subcommand

from utils.data import store
from models import MogiApplicationContext
from utils.decorators import is_admin

from fuzzywuzzy import process


class select_image(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @message_command(name="Select Image")
    async def select_image(self, ctx: MogiApplicationContext, message: Message):
        image_url = ""
        for a in message.attachments:
            if a.content_type and a.content_type.startswith("image/"):
                image_url = a.url
            # fallback on filename extension if content_type missing
            if any(
                a.filename.lower().endswith(ext)
                for ext in (".png", ".jpg", ".jpeg", ".gif", ".webp")
            ):
                image_url = a.url

        if not image_url:
            await ctx.respond(
                "No image attachment found in that message.", ephemeral=True
            )
            return

        await store.set_bytes(ctx.guild_id, ctx.author.id, image_url, message.jump_url)
        await ctx.respond(
            "Saved that image for you. Use `/table view` to view it or `/table clear` to clear it.",
            ephemeral=True,
        )

    @subcommand("table", independent=True)
    @slash_command(name="view", description="Show the image you selected earlier")
    async def use_image(self, ctx: MogiApplicationContext):
        record = await store.get_bytes(ctx.guild_id, ctx.author.id)
        if not record:
            await ctx.respond(
                "You haven't selected an image yet (or it expired). Right-click a message → Apps → Select Image.",
                ephemeral=True,
            )
            return

        embed = Embed(title="Your selected image")
        embed.description = f"Source: [jump]({record['source']})"
        embed.set_image(url=record["image_url"])
        await ctx.respond(embed=embed)

    @subcommand("table", independent=True)
    @slash_command(name="clear", description="Clear your saved image")
    async def clear_image(self, ctx: MogiApplicationContext):
        await store.clear(ctx.guild_id, ctx.author.id)
        await ctx.respond("Cleared your saved image.", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(select_image(bot))
