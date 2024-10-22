import math
import random
import discord
from discord import Interaction
from discord.ui import Button, View
from discord.utils import get
from utils.models.mogi import Mogi, PlayerProfile
from utils.mogis import get_mogi
from config import GUILD_IDS
from main import bot

def get_button_style(format: int, player_count: int) -> discord.ButtonStyle:
    if player_count % format == 0 and player_count > format:
        return discord.ButtonStyle.blurple
    return discord.ButtonStyle.gray 

def create_button(label: str, mogi: Mogi) -> Button:

    FORMAT_BUTTON_INT = int(label.lower()[0]) if label.lower()[0].isnumeric() else 1

    async def button_callback(interaction: Interaction):
        await interaction.response.defer()

        # Check if the user can vote
        if not (
            mogi.isVoting
            and len(mogi.players) >= FORMAT_BUTTON_INT
            and len(mogi.players) % FORMAT_BUTTON_INT == 0
            and (interaction.user.id in [player.discord_id for player in mogi.players])
            and interaction.user.id not in mogi.voters
        ): return await interaction.respond("Can't vote on that", ephemeral=True)
        
        # cast vote
        mogi.votes[label.lower()] += 1
        mogi.voters.append(interaction.user.id)

        # respond
        await interaction.respond(f"Voted for {label}", ephemeral=True)

        # check if vote is decided
        if not (
            len(mogi.voters) >= len(mogi.players)) or not (
            mogi.votes[max(mogi.votes, key=mogi.votes.get)]
            >= math.floor(len(mogi.players) / 2) + 1
        ): return
        
        # get winning format
        max_score = max(mogi.votes.values())
        winners = [player for player, score in mogi.votes.items() if score == max_score]
        
        MOGI_FORMAT = None
        FORMAT_STR = None

        if len(winners) > 1:
            await interaction.channel.send(f"# Vote is tied between {' and '.join(winners)}, choosing randomly...")
            
            chosen_winner = random.choice(winners)
            MOGI_FORMAT = int(chosen_winner[0]) if chosen_winner[0].isnumeric() else 1
            FORMAT_STR = chosen_winner
        else:
            MOGI_FORMAT = int(winners[0]) if winners[0].isnumeric() else 1
            FORMAT_STR = winners[0]

        # start playing mogi
        mogi.play(MOGI_FORMAT)

        lineup = ""
        for i, team in enumerate(mogi.teams):
                lineup += f"{i}. {', '.join([f'<@{player.discord_id}>' for player in team])}\n"

        return await interaction.message.channel.send(
             f"# Mogi starting!\n## Format: {FORMAT_STR}\n### Lineup:\n{lineup}"
        )
    
    button = Button(label=label, style=get_button_style(FORMAT_BUTTON_INT, len(mogi.players)), custom_id=label.lower())
    button.callback = button_callback
    return button

def create_button_view(button_labels: list[str], mogi: Mogi) -> View:
    view = View()
    for label in button_labels:
        view.add_item(create_button(label, mogi))
    return view

