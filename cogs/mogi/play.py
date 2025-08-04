from discord import (
    slash_command,
    SlashCommandGroup,
    AllowedMentions,
    Option,
)
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from utils.command_helpers.vote_factory import create_vote_button_view
from utils.decorators.checks import (
    is_mogi_in_progress,
    is_mogi_not_in_progress,
    is_mogi_manager,
)
from models.VoteModel import Vote
from utils.command_helpers.confirm import confirmation
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
        await ctx.defer()

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

        ctx.mogi.vote = Vote()

        async def send_vote():
            ctx.mogi.isPlaying = True
            message = await ctx.respond(
                f"Voting start!\nSelect a Format, or `Random Teams` first if you want it! {ctx.inmogi_role.mention}",
                view=create_vote_button_view(
                    FORMATS, ctx.mogi, extra_buttons=["Mini", "Random Teams"]
                ),
                allowed_mentions=AllowedMentions(roles=True),
            )
            response = await message.original_response()
            ctx.mogi.vote.voting_message_id = response.id

        async def pick_server():
            if not ctx.mogi.room:
                best_server = await get_best_server(ctx=ctx, mogi=ctx.mogi)
                ctx.mogi.room = best_server
            await ctx.channel.send(
                f"# Yuzu Server: {ctx.mogi.room.name}\nUse `/password`"
            )

        async def send_mogi_start(winning_format: str, random_teams: bool):
            format_int: int = (
                int(winning_format[0]) if winning_format[0].isdigit() else 1
            )

            # Create the lineup message by teams
            lineup = ""
            for i, team in enumerate(ctx.mogi.teams):
                lineup += f"{i}. {', '.join([f'<@{player.discord_id}>' for player in team])}\n"

            # Send the lineup, show the mogi has started
            await ctx.send(
                f"# Mogi starting!\n## Format: {'RANDOM' if random_teams and format_int != 1 else ''} {winning_format.upper()} Mogi\n### Lineup:\n{lineup}"
            )

        ctx.mogi.vote.add_setup_handler(send_vote)
        ctx.mogi.vote.add_setup_handler(pick_server)

        ctx.mogi.vote.add_cleanup_handler(send_mogi_start)
        ctx.mogi.vote.add_cleanup_handler(
            lambda *args, **kwargs: apply_team_roles(ctx=ctx, mogi=ctx.mogi)
        )

        await ctx.mogi.vote.start()

    @start.command(name="force")
    @is_mogi_not_in_progress()
    @is_mogi_manager()
    async def force(
        self,
        ctx: MogiApplicationContext,
        format: str = Option(str, choices=["Mini"] + FORMATS),
        random_teams: bool = Option(bool, required=False),
    ):
        # no mogi open
        if not ctx.mogi:
            return await ctx.respond("No open mogi in this channel", ephemeral=True)
        # mogi already started
        if ctx.mogi.isPlaying or ctx.mogi.vote:
            return await ctx.respond("Mogi already started", ephemeral=True)
        # not enough players
        if len(ctx.mogi.players) < 6 and not FLAGS["no_min_players"]:
            return await ctx.respond("Not enough players to start", ephemeral=True)

        ctx.mogi.play(
            int(format[0]) if format[0].isnumeric() else 1, random_teams=random_teams
        )
        if format == "Mini":
            ctx.mogi.is_mini = True

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

        if ctx.mogi.vote and ctx.mogi.vote.voting_message_id:
            try:
                await (
                    await ctx.channel.fetch_message(ctx.mogi.vote.voting_message_id)
                ).delete()
            except:
                pass
        ctx.mogi.stop()
        await ctx.respond("Mogi has been stopped")

        # remove all team roles
        await remove_team_roles(ctx=ctx)

    @slash_command(name="votes", description="Remind players to vote")
    @is_mogi_in_progress()
    async def votes(self, ctx: MogiApplicationContext):

        if not ctx.mogi.vote:
            return await ctx.respond("No vote found")

        if len(ctx.mogi.players) == ctx.mogi.vote.voters:
            return await ctx.respond("All players have voted")

        not_voted_str = ""

        if FLAGS["show_votes"]:
            most_votes = max(ctx.mogi.vote.votes.values())
            max_votes = [
                key
                for key in ctx.mogi.vote.votes.keys()
                if ctx.mogi.vote.votes[key] == most_votes
            ]
            if max_votes:
                not_voted_str += "Most voted so far:\n"
                for key in max_votes:
                    not_voted_str += key + "\n"
                runner_ups = [
                    key
                    for key in ctx.mogi.vote.votes.keys()
                    if ctx.mogi.vote.votes[key] == most_votes - 1
                ]
                if runner_ups:
                    not_voted_str += "\nRunner ups:\n"
                    for key in runner_ups:
                        not_voted_str += key + "\n"
            not_voted_str += "\n"

        not_voted_str += "Missing votes from:\n"
        hasnt_voted = []
        for player in ctx.mogi.players:
            if player.discord_id not in ctx.mogi.vote.voters:
                hasnt_voted.append(f"<@{player.discord_id}>")

        not_voted_str += "\n".join(hasnt_voted)

        message = f"{not_voted_str}\n\n"

        if ctx.mogi.vote.voting_message_id:
            voting_message = await ctx.channel.fetch_message(
                ctx.mogi.vote.voting_message_id
            )
            message += (
                f"{voting_message.jump_url}\nClick the above link to go to the vote!"
            )

        await ctx.respond(
            message,
        )


def setup(bot: commands.Bot):
    bot.add_cog(stop(bot))
