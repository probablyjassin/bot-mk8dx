import discord
from discord import Interaction
from discord.ui import Button, View

from models.MogiModel import Mogi


def get_vote_button_style(format: int, player_count: int) -> discord.ButtonStyle:
    if player_count % format == 0 and player_count > format:
        return discord.ButtonStyle.blurple
    return discord.ButtonStyle.gray


def create_format_vote_button(mogi: Mogi, label: str, is_extra: bool = False) -> Button:

    FORMAT_BUTTON_INT = int(label[0]) if label[0].isnumeric() else 1

    async def custom_callback(interaction: Interaction):
        vote_func = None
        if is_extra:
            vote_func = mogi.vote.cast_vote_extra
        else:
            vote_func = mogi.vote.cast_vote_format
        response = await vote_func(mogi=mogi, user_id=interaction.user.id, choice=label)
        message = f"Voted for {label}"
        if not response:
            message = "Can't vote on that"
        await interaction.respond(message, ephemeral=True)

    button_style = get_vote_button_style(FORMAT_BUTTON_INT, len(mogi.players))
    if is_extra:
        button_style = discord.ButtonStyle.green
    button = Button(
        label=label,
        style=button_style,
        custom_id=label.lower(),
    )
    button.callback = custom_callback
    return button


def create_vote_button_view(
    button_labels: list[str], mogi: Mogi, extra_buttons: list[str] = None
) -> View:
    """
    Creates a View object with buttons based on the provided labels and Mogi instance.
    These buttons each have a callback function with the complex logic for starting the mogi if needed.
    Args:
        button_labels (`list[str]`): A list of labels for the buttons to be created.
        mogi (`Mogi`): An instance of the Mogi class to be associated with each button.
        extra_buttons (`list[str]`, optional): Additional buttons to add on a new row.
    Returns:
        View: A View object containing the created buttons.
    """

    class VoteButtonView(View):
        def __init__(self):
            super().__init__(timeout=None)

    view = VoteButtonView()

    for label in button_labels:
        button = create_format_vote_button(mogi, label)
        view.add_item(button)

    for label in extra_buttons:
        button = create_format_vote_button(mogi, label, is_extra=True)
        view.add_item(button)

    return view
