import json
from discord import slash_command
from discord.ext import commands

from models import MogiApplicationContext

from utils.decorators.checks import _is_at_least_role
from utils.decorators import LoungeRole, with_player
from utils.command_helpers import get_best_server

from utils.data import guild_manager


class password(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(
        name="password", description="Get the password for the server your mogi uses."
    )
    @with_player()
    async def password(self, ctx: MogiApplicationContext):
        passwords: dict | None = None
        with open("state/passwords.json", "r", encoding="utf-8") as f:
            passwords: dict | None = json.load(f)

        # for guilds
        if (
            len(guild_manager.playing_guilds)
            and ctx.get_lounge_role("Admin") not in ctx.user.roles
        ):
            for guild in guild_manager.playing_guilds:
                if ctx.player in guild.playing:
                    best_server = await get_best_server(ctx=ctx, mogi=ctx.mogi)

                    pwd = passwords.get(best_server.name)

                    response = (
                        f"Password: `{pwd}`"
                        if pwd
                        else "Password for your mogi's room not found, please contact a Mogi Manager or Admin."
                    )

                    return await ctx.respond(
                        response,
                        ephemeral=True,
                    )

        if (not ctx.mogi or not ctx.mogi.room) and ctx.get_lounge_role(
            "Admin"
        ) not in ctx.user.roles:
            return await ctx.respond(
                "The mogi doesn't have a yuzu server assigned yet. This might be because the mogi hasn't started yet."
            )

        if (
            not ctx.mogi or (ctx.player not in ctx.mogi.players)
        ) and ctx.get_lounge_role("Admin") not in ctx.user.roles:
            return await ctx.respond(
                "You're not in this mogi. You need to wait for a mogi to open and then join it (`/join`)"
            )

        if _is_at_least_role(ctx, LoungeRole.MOGI_MANAGER) or not ctx.mogi.room:
            return await ctx.respond(
                "\n".join(
                    [
                        f"{server_name}: `{passwords[server_name]}`"
                        for server_name in passwords
                    ]
                ),
                ephemeral=True,
            )

        if not ctx.mogi or not ctx.mogi.room:
            return await ctx.respond(
                "The mogi doesn't have a yuzu server assigned yet. This might be because the mogi hasn't started yet."
            )

        if ctx.player not in ctx.mogi.players:
            return await ctx.respond(
                "You're not in this mogi. You need to wait for a mogi to open and then join it (`/join`)"
            )

        pwd = passwords.get(ctx.mogi.room.name)

        response = (
            f"{ctx.mogi.room.name}\nPassword: `{pwd}`"
            if pwd
            else "Password for your mogi's room not found, please contact a Mogi Manager or Admin."
        )

        await ctx.respond(
            response,
            ephemeral=True,
        )


def setup(bot: commands.Bot):
    bot.add_cog(password(bot))
