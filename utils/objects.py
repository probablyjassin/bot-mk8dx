import discord
from discord import Guild, TextChannel, Role
from discord.utils import get
from config import GUILD_IDS, ERROR_CHANNEL_ID, REGISTER_CHANNEL_ID
from main import bot

async def get_main_guild() -> Guild:
    return await bot.fetch_guild(GUILD_IDS[0])

async def get_register_channel() -> TextChannel:
    return await bot.fetch_channel(REGISTER_CHANNEL_ID)

async def get_error_channel() -> TextChannel:
    return await bot.fetch_channel(ERROR_CHANNEL_ID)

async def get_lounge_role(name: str) -> Role:
    return get((await get_main_guild()).roles, name=name)

async def get_inmogi_role() -> Role:
    return get((await get_main_guild()).roles, name="InMogi")

async def get_mogi_manager_role() -> Role:
    return get((await get_main_guild()).roles, name="Mogi Manager")

async def get_moderator_role() -> Role:
    return get((await get_main_guild()).roles, name="Moderator")

async def get_admin_role() -> Role:
    return get((await get_main_guild()).roles, name="Admin")
