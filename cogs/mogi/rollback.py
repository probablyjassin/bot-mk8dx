from discord import slash_command
from discord.ext import commands

from pycord.multicog import subcommand

from utils.decorators import is_admin
from utils.command_helpers import create_embed, confirmation, get_awaited_message

from models import MogiApplicationContext, MogiHistoryData

from services.mogis import get_latest_mogi
from services.players import find_player_profiles_by_ids


class rollback(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @subcommand(group="manage", independent=True)
    @is_admin()
    @slash_command(
        name="rollback",
        description="Admin only: roll back the last mogi's results",
    )
    async def rollback(self, ctx: MogiApplicationContext):
        await ctx.defer()

        latest_mogi: MogiHistoryData | None = await get_latest_mogi()
        if not latest_mogi:
            return await ctx.respond("Couldn't find a latest mogi in the database.")

        all_players = await find_player_profiles_by_ids(latest_mogi.player_ids)

        last_mogi_embed = create_embed(
            title="Latest mogi:",
            description="You are trying to revert the following mogi:",
            fields={
                "Started at:": f"<t:{latest_mogi.started_at}>",
                "Finished at:": f"<t:{latest_mogi.finished_at}>",
                "Players:": "\n".join(
                    f"<@{player}>" for player in latest_mogi.player_ids
                ),
                "MMR changes (in player order):": "\n".join(
                    [str(score) for score in latest_mogi.results]
                ),
            },
        )

        erase_mogi_fully: bool = True

        if await confirmation(
            ctx=ctx,
            text="# React ✅ to overwrite the mogi with new fixed scores\n# OR ❌ to erase it completely!",
            user_id=ctx.user.id,
            embed=last_mogi_embed,
        ):
            erase_mogi_fully = False

            # Ask user to input the new table string
            await ctx.respond(
                "Please send the corrected table string in this channel.\n"
                "You have 60 seconds to respond."
            )

            tablestring = await get_awaited_message(
                bot=self.bot, ctx=ctx, target_channel=ctx.channel
            )

            if not tablestring:
                return await ctx.respond(
                    "No table string provided. Rollback cancelled."
                )

            await ctx.respond(
                f"Table string received:\n```\n{tablestring}\n```\n"
                "The rest is not implemented yet"
            )

            # TODO: add logic to recreate the table and collect points

        else:
            # TODO: erase completely
            await ctx.respond("This is not implemented yet.")

        return await ctx.respond("WIP")


def setup(bot: commands.Bot):
    bot.add_cog(rollback(bot))
