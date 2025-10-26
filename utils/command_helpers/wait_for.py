import asyncio

from discord import TextChannel, Bot
from models import MogiApplicationContext


async def get_awaited_message(
    bot: Bot, ctx: MogiApplicationContext, target_channel: TextChannel
) -> str:
    try:
        message = await bot.wait_for(
            "message",
            check=lambda m: m.author == ctx.author and m.channel == target_channel,
            timeout=60.0,
        )
        return message.content
    except asyncio.TimeoutError:
        await ctx.respond("You took too long to respond!")
        return ""
