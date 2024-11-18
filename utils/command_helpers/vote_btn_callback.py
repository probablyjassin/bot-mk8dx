import math
import random
import asyncio

from discord import Interaction

from models.MogiModel import Mogi

voters_lock = asyncio.Lock()


async def button_callback(
    interaction: Interaction, mogi: Mogi, FORMAT_BUTTON_INT, label
):
    await interaction.response.defer()

    # Check if the user can vote
    if not (
        mogi.isVoting
        and len(mogi.players) >= FORMAT_BUTTON_INT
        and len(mogi.players) % FORMAT_BUTTON_INT == 0
        and (interaction.user.id in [player.discord_id for player in mogi.players])
        and interaction.user.id not in mogi.voters
    ):
        return await interaction.respond("Can't vote on that", ephemeral=True)

    # cast vote
    async with voters_lock:
        mogi.votes[label.lower()] += 1
        mogi.voters.append(interaction.user.id)

        # respond
        await interaction.respond(f"Voted for {label}", ephemeral=True)
        await interaction.channel.send(
            f"-# Debug: {interaction.user.name} voted for {label}"
        )

        # check if vote is decided
        all_vote_counts = sorted(mogi.votes.values(), reverse=True)
        second_highest_votes = all_vote_counts[1] if len(all_vote_counts) > 1 else 0

        isDecided = len(mogi.voters) >= len(mogi.players) or max(
            mogi.votes.values()
        ) > (second_highest_votes + (len(mogi.players) - len(mogi.voters)))

        if not isDecided:
            return

        # get winning format
        max_score = max(mogi.votes.values())
        winners = [player for player, score in mogi.votes.items() if score == max_score]

        MOGI_FORMAT = None
        FORMAT_STR = None

        if len(winners) > 1:
            await interaction.channel.send(
                f"# Vote is tied between {' and '.join(winners)}, choosing randomly..."
            )

            chosen_winner = random.choice(winners)
            MOGI_FORMAT = int(chosen_winner[0]) if chosen_winner[0].isnumeric() else 1
            FORMAT_STR = chosen_winner
        else:
            MOGI_FORMAT = int(winners[0][0]) if winners[0][0].isnumeric() else 1
            FORMAT_STR = winners[0]

        # start playing mogi
        mogi.play(MOGI_FORMAT)

        lineup = ""
        for i, team in enumerate(mogi.teams):
            lineup += (
                f"{i}. {', '.join([f'<@{player.discord_id}>' for player in team])}\n"
            )

        return await interaction.message.channel.send(
            f"# Mogi starting!\n## Format: {FORMAT_STR}\n### Lineup:\n{lineup}"
        )
