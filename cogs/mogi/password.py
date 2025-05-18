import json
from discord import slash_command
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext

from utils.decorators.checks import is_mogi_in_progress
from utils.decorators.player import with_player
from utils.decorators.checks import LoungeRole, _is_at_least_role


class password(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(
        name="password", description="Get the password for the server your mogi uses."
    )
    @with_player()
    async def password(self, ctx: MogiApplicationContext):

        if (not ctx.mogi or not ctx.mogi.room) and ctx.get_lounge_role(
            "Admin"
        ) not in ctx.user.roles:
            return await ctx.respond(
                "The mogi is either not open or doesn't have a yuzu server assigned yet because it didn't start yet."
            )

        if (
            not ctx.mogi or (ctx.player not in ctx.mogi.players)
        ) and ctx.get_lounge_role("Admin") not in ctx.user.roles:
            return await ctx.respond("You're not in this mogi")

        passwords: dict | None = None
        with open("state/passwords.json", "r", encoding="utf-8") as f:
            passwords: dict | None = json.load(f)

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
