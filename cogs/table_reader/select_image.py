from discord import slash_command, message_command, Message, Embed
from discord.ext import commands
from pycord.multicog import subcommand

from utils.data import store
from utils.decorators import is_mogi_manager
from models import MogiApplicationContext


class select_image(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @message_command(name="Select Image")
    @is_mogi_manager()
    async def select_image(self, ctx: MogiApplicationContext, message: Message):
        selected = None
        for a in message.attachments:
            if a.content_type and a.content_type.startswith("image/"):
                selected = a
                break
            # fallback on filename extension if content_type missing
            if any(
                a.filename.lower().endswith(ext)
                for ext in (".png", ".jpg", ".jpeg", ".gif", ".webp")
            ):
                selected = a
                break

        if not selected:
            await ctx.respond(
                "No image attachment found in that message.", ephemeral=True
            )
            return

        # Read bytes from the attachment directly (avoids an extra HTTP client)
        image_bytes = await selected.read()
        await store.set_bytes(
            guild_id=ctx.guild_id,
            user_id=ctx.author.id,
            image_bytes=image_bytes,
            filename=selected.filename,
            content_type=selected.content_type,
            source_message_url=message.jump_url,
            image_url=selected.url,
        )
        await ctx.respond(
            "Saved that image for you. Use `/table view` to view it or `/table clear` to clear it.",
            ephemeral=True,
        )

    @subcommand("table", independent=True)
    @slash_command(name="view", description="Show the image you selected earlier")
    @is_mogi_manager()
    async def use_image(self, ctx: MogiApplicationContext):
        record = await store.get(ctx.guild_id, ctx.author.id)
        if not record:
            await ctx.respond(
                "You haven't selected an image yet (or it expired). Right-click a message → Apps → Select Image.",
                ephemeral=True,
            )
            return

        embed = Embed(title="Your selected image")
        if record.get("source"):
            embed.description = f"Source: [jump]({record['source']})"

        # Prefer bytes (more reliable than potentially expired URLs)
        file = await store.to_discord_file(ctx.guild_id, ctx.author.id)
        if file:
            embed.set_image(url=f"attachment://{file.filename}")
            await ctx.respond(embed=embed, file=file)
            return

        # Fallback to the original URL if bytes aren't cached
        if record.get("image_url"):
            embed.set_image(url=record["image_url"])
            await ctx.respond(embed=embed)
            return

        await ctx.respond("No cached image found.", ephemeral=True)

    @subcommand("table", independent=True)
    @slash_command(name="clear", description="Clear your saved image")
    @is_mogi_manager()
    async def clear_image(self, ctx: MogiApplicationContext):
        await store.clear(ctx.guild_id, ctx.author.id)
        await ctx.respond("Cleared your saved image.", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(select_image(bot))
