import discord
from discord import Guild, TextChannel, Role
from discord.utils import get
from config import GUILD_ID, ERROR_CHANNEL_ID, REGISTER_CHANNEL_ID
from main import bot

async def get_guild() -> Guild:
    return await bot.fetch_guild(GUILD_ID)

async def get_register_channel() -> TextChannel:
    return await bot.fetch_channel(REGISTER_CHANNEL_ID)

async def get_error_channel() -> TextChannel:
    return await bot.fetch_channel(ERROR_CHANNEL_ID)

async def get_lounge_role(rank: str) -> Role:
    return get((await get_guild()).roles, name=f"Lounge - {rank}")

async def get_inmogi_role() -> Role:
    return get((await get_guild()).roles, name="InMogi")
