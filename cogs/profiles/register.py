from discord import slash_command, ApplicationContext, Member
from discord.utils import get
from discord.ext import commands

from logger import setup_logger
from utils.data.database import db_players, db_archived
from config import GUILD_IDS, REGISTER_CHANNEL_ID

from bson.int64 import Int64
import time


# TODO: Log registers to lounge.log and log channel
lounge_logger = setup_logger(__name__, "lounge.log", "a")


class register(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.MAIN_GUILD = get(self.bot.guilds, id=GUILD_IDS[0])
        self.REGISTER_CHANNEL = get(self.MAIN_GUILD.channels, id=REGISTER_CHANNEL_ID)

    @slash_command(
        name="register",
        description="Register for playing in Lounge",
        guild_ids=GUILD_IDS,
    )
    async def register(self, ctx: ApplicationContext):
        await ctx.defer()

        if ctx.channel_id != self.REGISTER_CHANNEL.id:
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
        if get(self.MAIN_GUILD.roles, name="Lounge Player") in member.roles:
            return await ctx.respond(
                "You already have the Lounge Player role even though you don't have a player profile. Please ask a moderator for help.",
                ephemeral=True,
            )
        try:
            db_players.insert_one(
                {
                    "name": username,
                    "mmr": 2000,
                    "discord_id": Int64(member.id),
                    "joined": round(time.time()),
                    "history": [],
                },
            )
        except:
            return await ctx.respond(
                "Some error occured creating your player record. Please ask a moderator.",
                ephemeral=True,
            )
        await member.add_roles(get(self.MAIN_GUILD.roles, name="Lounge Player"))
        # await member.add_roles(get(self.MAIN_GUILD.roles, name="Lounge - Silver"))
        await ctx.respond(
            f"{member.mention} is now registered for Lounge as {username}\n You can view your profile at https://mk8dx-yuzu.github.io/{username}",
            ephemeral=False,
        )


def setup(bot: commands.Bot):
    bot.add_cog(register(bot))
