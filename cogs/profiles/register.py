import time
import datetime
import unicodedata

from discord import (
    slash_command,
    Member,
    User,
    Color,
    AllowedMentions,
)
from discord.ext import commands

from models import MogiApplicationContext
from utils.data._database import db_players, db_archived, client
from utils.command_helpers import create_embed, VerificationView
from utils.maths.readable_timediff import readable_timedelta

from logger import setup_logger

from bson.int64 import Int64
from config import LOG_CHANNEL_ID

lounge_logger = setup_logger(__name__, "lounge.log", "a", console=False)


class register(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(
        name="register",
        description="Register for playing in Lounge",
    )
    @commands.cooldown(1, 7200, commands.BucketType.user)
    async def register(
        self,
        ctx: MogiApplicationContext,
    ):
        await ctx.defer(ephemeral=True)

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

        ## more or less temporary code for people who come back after the season reset
        existingPlayer = (
            client.get_database("season-3-lounge")
            .get_collection("players")
            .find_one({"discord_id": Int64(ctx.author.id)})
        )
        if existingPlayer:
            return await ctx.respond(
                "You played in Season 3 but left the server since. Please contact an Admin to get your Profile migrated",
                ephemeral=True,
            )

        # username shenanigans
        def normalize_fancy_unicode(text: str) -> str:
            result = []
            for char in text:
                # Try to get the base character from the Unicode name
                try:
                    name = unicodedata.name(char)
                    if "CAPITAL" in name:
                        base_char = name.split()[-1]
                        if len(base_char) == 1 and base_char.isalpha():
                            result.append(base_char.upper())
                    elif "SMALL" in name:
                        base_char = name.split()[-1]
                        if len(base_char) == 1 and base_char.isalpha():
                            result.append(base_char.lower())
                    elif char.isalnum():
                        result.append(char)
                except ValueError:
                    # character has no Unicode name, skip it
                    pass
            return "".join(result)

        username = normalize_fancy_unicode(ctx.interaction.user.display_name).lower()
        if username == "":
            username = ctx.interaction.user.name.lower()

        if db_players.find_one({"name": username}):
            return await ctx.respond(
                "This username is already taken. Try changing your server display name or ask a moderator for help.",
                ephemeral=True,
            )

        member: Member | User = ctx.user
        if ctx.get_lounge_role("Lounge Player") in member.roles:
            return await ctx.respond(
                "You already have the Lounge Player role "
                "even though you don't have a player profile. "
                "Ask a moderator for help.",
                ephemeral=True,
            )

        # Create verification dropdown
        embed = create_embed(
            title="🔍 Registration Verification",
            description=f"To complete your registration as **{username}**, please select the right option below:",
            color=Color.blue(),
        )

        view = VerificationView(ctx.user.id)
        await ctx.followup.send(embed=embed, view=view, ephemeral=True)

        # Wait for verification result
        verification_passed = await view.wait_for_answer()

        if not verification_passed:
            await ctx.followup.send(
                "❌ Verification failed. Please read all the relevant channels FULLY and try again later.",
                ephemeral=True,
            )
            return

        # Verification passed - proceed with registration
        try:
            db_players.insert_one(
                {
                    "name": username,
                    "discord_id": Int64(member.id),
                    "mmr": 2000,
                    "history": [],
                    "joined": round(time.time()),
                    "formats": {str(i): 0 for i in range(7)},
                },
            )
        except Exception as e:
            return await ctx.respond(
                f"Some error occured creating your player record. Please ask a moderator: {e}",
                ephemeral=True,
            )

        # write to logfile
        lounge_logger.info(
            f"{member.display_name} ({member.id}) registered as {username} | Locale: {ctx.locale}"
        )

        # add roles
        lounge_player_role = ctx.get_lounge_role("Lounge Player")
        lounge_silver_role = ctx.get_lounge_role("Lounge - Silver")
        if lounge_player_role not in ctx.user.roles:
            await member.add_roles(
                ctx.get_lounge_role("Lounge Player"), reason="Registered for Lounge"
            )
        if lounge_silver_role not in ctx.user.roles:
            await member.add_roles(
                ctx.get_lounge_role("Lounge - Silver"), reason="Registered for Lounge"
            )

        # done
        await ctx.respond(
            f"{member.mention} is now registered for Lounge as {username}\n You can view your profile at https://mk8dx-yuzu.github.io/{username}",
            ephemeral=True,
        )

        # detect suspicious activity
        now = datetime.datetime.now(datetime.timezone.utc)
        delta_joined = now - ctx.user.joined_at
        delta_created = now - ctx.user.created_at

        is_sus = delta_joined.total_seconds() < 600 or delta_created.days < 60
        is_VERY_sus = delta_joined.total_seconds() < 90 or delta_created.days < 30

        if is_sus:
            embed = create_embed(
                title="⚠️ Warning - potentially suspicious new Lounge Player",
                description=f"{ctx.user.mention} registered **{readable_timedelta(delta_joined)}** after joining.",
                fields={
                    "Account created:": readable_timedelta(delta_created),
                    "Lounge Name:": username,
                    "User Locale:": ctx.locale,
                },
                color=(Color.red() if is_VERY_sus else Color.yellow()),
                inline=False,
            )
            mogi_manager_role = ctx.get_lounge_role("Mogi Manager")

            log_channel = await self.bot.fetch_channel(LOG_CHANNEL_ID)

            await log_channel.send(
                mogi_manager_role.mention,
                embed=embed,
                allowed_mentions=AllowedMentions(roles=is_VERY_sus),
            )


def setup(bot: commands.Bot):
    bot.add_cog(register(bot))
