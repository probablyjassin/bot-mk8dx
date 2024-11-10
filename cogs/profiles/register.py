from discord import slash_command, Member
from discord.utils import get
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from utils.data.database import db_players, db_archived

from logger import setup_logger

from bson.int64 import Int64
import time


lounge_logger = setup_logger(__name__, "lounge.log", "a", console=False)


class register(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(
        name="register",
        description="Register for playing in Lounge",
    )
    async def register(self, ctx: MogiApplicationContext):
        await ctx.defer()

        if ctx.channel_id != ctx.register_channel.id:
            return await ctx.respond(
                "You're not in the right channel for this command.", ephemeral=True
            )

        existingPlayer = (
            db_players.find_one({"discord_id": Int64(ctx.author.id)})
            or db_archived.find_one({"discord_id": Int64(ctx.author.id)})
            or None
        )
        if existingPlayer:
            return await ctx.respond(
                "You are already registered for Lounge.\nIf your Profile is archived or you're missing the Lounge roles due to rejoining the server, contact a moderator.",
                ephemeral=True,
            )

        username = "".join(
            e for e in ctx.interaction.user.display_name.lower() if e.isalnum()
        )
        if username == "":
            username = ctx.interaction.user.name.lower()

        if db_players.find_one({"name": username}):
            return await ctx.respond(
                "This username is already taken. Try changing your server display name or ask a moderator for help.",
                ephemeral=True,
            )

        member: Member = ctx.user
        if ctx.get_lounge_role("Lounge Player") in member.roles:
            return await ctx.respond(
                "You already have the Lounge Player role"
                "even though you don't have a player profile."
                "Ask a moderator for help.",
                ephemeral=True,
            )
        try:
            db_players.insert_one(
                {
                    "name": username,
                    "discord_id": Int64(member.id),
                    "mmr": 2000,
                    "history": [],
                    "joined": round(time.time()),
                },
            )
        except:
            return await ctx.respond(
                "Some error occured creating your player record. Please ask a moderator.",
                ephemeral=True,
            )
        await member.add_roles(ctx.get_lounge_role("Lounge Player"))
        await member.add_roles(ctx.get_lounge_role("Lounge - Silver"))
        await ctx.respond(
            f"{member.mention} is now registered for Lounge as {username}\n You can view your profile at https://mk8dx-yuzu.github.io/{username}",
            ephemeral=False,
        )
        lounge_logger.info(f"{member.display_name} registered as {username}")


def setup(bot: commands.Bot):
    bot.add_cog(register(bot))
