from discord import slash_command, Message, Option
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from utils.command_helpers.vote_factory import create_button_view
from utils.command_helpers.command_groups import start
from utils.command_helpers.checks import (
    is_mogi_in_progress,
    is_mogi_not_in_progress,
    is_mogi_manager,
)


class stop(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @start.command(name="vote")
    @is_mogi_not_in_progress()
    async def vote(self, ctx: MogiApplicationContext):

        # not enough players
        if len(ctx.mogi.players) < 0:  # DEBUG: remember to change this in production
            return await ctx.respond("Not enough players to start", ephemeral=True)
        # more than 12 players
        if len(ctx.mogi.players) > 12:
            return await ctx.respond("Cant start with more than 12 players")
        # user not in the mogi
        if not ctx.inmogi_role in ctx.user.roles:
            return await ctx.respond(
                "You can't start a mogi you aren't in", ephemeral=True
            )

        ctx.mogi.isVoting = True

        view = create_button_view(["FFA", "2v2", "3v3", "4v4", "6v6"], ctx.mogi)
        message = await ctx.respond(
            f"Voting start!\n ||{''.join([f'<@{player.discord_id}>' for player in ctx.mogi.players])}||",
            view=view,
        )
        response = await message.original_response()
        ctx.mogi.voting_message_id = response.id

    @start.command(name="force")
    @is_mogi_not_in_progress()
    @is_mogi_manager()
    async def force(
        self,
        ctx: MogiApplicationContext,
        format: str = Option(str, choices=["FFA", "2v2", "3v3", "4v4", "6v6"]),
    ):
        # no mogi open
        if not ctx.mogi:
            return await ctx.respond("No open mogi in this channel", ephemeral=True)
        # mogi already started
        if ctx.mogi.isPlaying or ctx.mogi.isVoting:
            return await ctx.respond("Mogi already started", ephemeral=True)

        ctx.mogi.play(int(format[0]) if format[0].isnumeric() else 1)

        lineup = ""
        for i, team in enumerate(ctx.mogi.teams):
            lineup += (
                f"{i}. {', '.join([f'<@{player.discord_id}>' for player in team])}\n"
            )

        await ctx.respond(f"Mogi started!\n{lineup}")

    @slash_command(name="stop", description="Halt the current mogi")
    @is_mogi_in_progress()
    async def stop(self, ctx: MogiApplicationContext):

        # user not in the mogi
        if not ctx.inmogi_role in ctx.user.roles:
            return await ctx.respond(
                "You can't stop a mogi you aren't in", ephemeral=True
            )

        ctx.mogi.stop()
        if ctx.mogi.voting_message_id:
            vote_msg: Message = await ctx.channel.fetch_message(
                ctx.mogi.voting_message_id
            )
            if vote_msg:
                await vote_msg.delete()
        await ctx.respond("Mogi has been stopped")


def setup(bot: commands.Bot):
    bot.add_cog(stop(bot))
