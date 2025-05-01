import discord
from discord import Interaction
from discord.ui import Button, View

from models.MogiModel import Mogi
from utils.command_helpers.vote_btn_callback import button_callback

import random


def get_button_style(format: int, player_count: int) -> discord.ButtonStyle:
    if player_count % format == 0 and player_count > format:
        return discord.ButtonStyle.blurple
    return discord.ButtonStyle.gray


def create_button(label: str, mogi: Mogi) -> Button:

    FORMAT_BUTTON_INT = int(label.lower()[0]) if label.lower()[0].isnumeric() else 1

    async def custom_callback(interaction: Interaction):
        await button_callback(
            interaction, mogi=mogi, FORMAT_BUTTON_INT=FORMAT_BUTTON_INT, label=label
        )

    button = Button(
        label=label,
        style=get_button_style(FORMAT_BUTTON_INT, len(mogi.players)),
        custom_id=label.lower(),
    )
    button.callback = custom_callback
    return button


def create_button_view(button_labels: list[str], mogi: Mogi) -> View:
    """
    Creates a View object with buttons based on the provided labels and Mogi instance.
    These buttons each have a callback function with the complex logic for starting the mogi if needed.
    Args:
        button_labels (`list[str]`): A list of labels for the buttons to be created.
        mogi (`Mogi`): An instance of the Mogi class to be associated with each button.
    Returns:
        View: A View object containing the created buttons.
    """

    class VoteButtonView(View):
        def __init__(self):
            super().__init__(timeout=None)

    view = VoteButtonView()
    for label in button_labels:
        view.add_item(create_button(label, mogi))
    return view
