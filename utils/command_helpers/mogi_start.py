import discord
from discord import Interaction
from discord.ui import Button, View

from models.MogiModel import Mogi
from utils.command_helpers.vote_btn_callback import button_callback


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
    view = View()
    for label in button_labels:
        view.add_item(create_button(label, mogi))
    return view
