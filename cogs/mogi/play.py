from discord import slash_command, SlashCommandGroup, AllowedMentions, Option
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from utils.command_helpers.vote_factory import create_vote_button_view
from utils.decorators.checks import (
    is_mogi_in_progress,
    is_mogi_not_in_progress,
    is_mogi_manager,
)
from utils.command_helpers.team_roles import apply_team_roles, remove_team_roles
from utils.command_helpers.server_region import get_best_server

from config import FORMATS, FLAGS


class stop(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    start = SlashCommandGroup(
        name="start",
        description="Start a mogi. Start voting or force (for mogi managers).",
    )

    @start.command(name="vote")
    @is_mogi_not_in_progress()
    async def vote(self, ctx: MogiApplicationContext):
        if FLAGS["hold_mogis"]:
            return await ctx.respond(
                "Because of maintenance, you cannot start mogis for just a few moments."
            )

        # not enough players
        if len(ctx.mogi.players) <= 6 and not FLAGS["no_min_players"]:
            return await ctx.respond("Not enough players to start", ephemeral=True)
        # more than 12 players
        if len(ctx.mogi.players) > 12:
            return await ctx.respond("Cant start with more than 12 players")
        # user not in the mogi
        if (
            not ctx.inmogi_role in ctx.user.roles
            and ctx.get_lounge_role("Mogi Manager") not in ctx.user.roles
        ):
            return await ctx.respond(
                "You can't start a mogi you aren't in", ephemeral=True
            )

        ctx.mogi.isVoting = True

        view = create_vote_button_view(FORMATS, ctx.mogi)

        message = await ctx.respond(
            f"Voting start!\n {ctx.inmogi_role.mention}",
            view=view,
            allowed_mentions=AllowedMentions(roles=True),
        )
        response = await message.original_response()
        ctx.mogi.voting_message_id = response.id

        # put the channel in slowmode during vote
        await ctx.channel.edit(slowmode_delay=15)

        # pick the server to play on
        if not ctx.mogi.room:
            best_server = await get_best_server(ctx=ctx, mogi=ctx.mogi)
            ctx.mogi.room = best_server
        await ctx.channel.send(f"# Yuzu Server: {ctx.mogi.room.name}\nUse `/password`")

    @start.command(name="force")
    @is_mogi_not_in_progress()
    @is_mogi_manager()
    async def force(
        self,
        ctx: MogiApplicationContext,
        format: str = Option(str, choices=FORMATS),
    ):
        # no mogi open
        if not ctx.mogi:
            return await ctx.respond("No open mogi in this channel", ephemeral=True)
        # mogi already started
        if ctx.mogi.isPlaying or ctx.mogi.isVoting:
            return await ctx.respond("Mogi already started", ephemeral=True)
        # not enough players
        if len(ctx.mogi.players) < 6 and not FLAGS["no_min_players"]:
            return await ctx.respond("Not enough players to start", ephemeral=True)

        ctx.mogi.play(int(format[0]) if format[0].isnumeric() else 1)

        lineup = ""
        for i, team in enumerate(ctx.mogi.teams):
            lineup += (
                f"{i}. {', '.join([f'<@{player.discord_id}>' for player in team])}\n"
            )

        await ctx.respond(f"Mogi started!\n{lineup}")

        # apply team roles
        await apply_team_roles(ctx=ctx, mogi=ctx.mogi)

    @slash_command(name="stop", description="Halt the current mogi")
    @is_mogi_in_progress()
    async def stop(self, ctx: MogiApplicationContext):

        # user not in the mogi (except for mogi managers)
        if (
            not ctx.inmogi_role in ctx.user.roles
            and ctx.get_lounge_role("Mogi Manager") not in ctx.user.roles
        ):
            return await ctx.respond(
                "You can't stop a mogi you aren't in", ephemeral=True
            )

        ctx.mogi.stop()
        if ctx.mogi.voting_message_id:
            try:
                await (
                    await ctx.channel.fetch_message(ctx.mogi.voting_message_id)
                ).delete()
            except:
                pass
        await ctx.respond("Mogi has been stopped")

        # disable slowmode
        await ctx.channel.edit(slowmode_delay=0)

        # remove all team roles
        await remove_team_roles(ctx=ctx)

    @slash_command(name="votes", description="Remind players to vote")
    @is_mogi_in_progress()
    async def votes(self, ctx: MogiApplicationContext):

        if not ctx.mogi.voting_message_id or not ctx.mogi.isVoting:
            return await ctx.respond("No vote found")

        if len(ctx.mogi.players) == ctx.mogi.voters:
            return await ctx.respond("All players have voted")

        not_voted_str = ""

        if FLAGS["show_votes"]:
            most_votes = max(ctx.mogi.votes.values())
            max_votes = [
                key
                for key in ctx.mogi.votes.keys()
                if ctx.mogi.votes[key] == most_votes
            ]
            if max_votes:
                not_voted_str += "Most voted so far:\n"
                for key in max_votes:
                    not_voted_str += key + "\n"
                runner_ups = [
                    key
                    for key in ctx.mogi.votes.keys()
                    if ctx.mogi.votes[key] == most_votes - 1
                ]
                if runner_ups:
                    not_voted_str += "\nRunner ups:\n"
                    for key in runner_ups:
                        not_voted_str += key + "\n"
            not_voted_str += "\n"

        not_voted_str += "Missing votes from:\n"
        hasnt_voted = []
        for player in ctx.mogi.players:
            if player.discord_id not in ctx.mogi.voters:
                hasnt_voted.append(f"<@{player.discord_id}>")

        not_voted_str += "\n".join(hasnt_voted)

        voting_message = await ctx.channel.fetch_message(ctx.mogi.voting_message_id)

        await ctx.respond(
            f"{not_voted_str}\n\n{voting_message.jump_url}\nClick the above link to go to the vote!",
        )


def setup(bot: commands.Bot):
    bot.add_cog(stop(bot))
