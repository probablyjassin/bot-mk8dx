import discord
from discord import Interaction
from discord.ui import Button, View

from models.MogiModel import Mogi

threshold = 0.6


def _vote_key(label: str) -> str:
    """Map a button label to the key used in Vote.votes / Vote.user_votes."""
    return "mini" if label == "Mini" else label


def _get_vote_count(label: str, mogi: Mogi) -> int:
    """Return the current vote count for a given button label."""
    if not mogi.vote:
        return 0
    return mogi.vote.votes.get(_vote_key(label), 0)


def _display_label(label: str, mogi: Mogi) -> str:
    """Return the button label with the current vote count appended."""
    count = _get_vote_count(label, mogi)
    return f"{label} ({count})" if count else label


def get_vote_button_style(format: int, player_count: int) -> discord.ButtonStyle:
    if player_count % format == 0 and player_count > format:
        return discord.ButtonStyle.blurple
    return discord.ButtonStyle.gray


def create_vote_button_view(
    button_labels: list[str], mogi: Mogi, extra_buttons: list[str] = None
) -> View:
    """
    Creates a View with vote buttons whose labels reflect the live vote counts.
    Clicking a button casts (or changes) the user's vote and refreshes the counts.

    Args:
        button_labels: Format buttons (e.g. FORMATS).
        mogi: The active Mogi instance.
        extra_buttons: Optional extra buttons (e.g. ["Mini", "Random Teams"]).
    Returns:
        A View containing all vote buttons.
    """
    extra_buttons = extra_buttons or []

    def _build_button(label: str, is_extra: bool) -> Button:
        format_int = int(label[0]) if label[0].isnumeric() else 1

        async def callback(interaction: Interaction):
            # prevent interaction errors when someone votes right as the vote already ended
            await interaction.response.defer(ephemeral=True)

            if not mogi.vote:
                return await interaction.followup.send(
                    "Vote is not active.", ephemeral=True
                )

            prev_key = mogi.vote.user_votes.get(interaction.user.id)

            vote_func = (
                mogi.vote.cast_vote_extra if is_extra else mogi.vote.cast_vote_format
            )
            success = await vote_func(
                mogi=mogi, user_id=interaction.user.id, choice=label
            )

            if not success:
                return await interaction.followup.send(
                    "Can't vote on that.", ephemeral=True
                )

            # Build the ephemeral confirmation message
            new_key = _vote_key(label)
            changed = prev_key is not None and prev_key != new_key
            if changed:
                msg = f"Changed vote to **{label}**."
            else:
                msg = f"Voted for **{label}**."

            await interaction.followup.send(msg, ephemeral=True)

            # Refresh button labels with updated counts (only while vote is still active)
            if mogi.vote and mogi.vote.is_active:
                try:
                    await interaction.message.edit(
                        view=create_vote_button_view(button_labels, mogi, extra_buttons)
                    )
                except Exception:
                    pass

        style = (
            discord.ButtonStyle.green
            if is_extra
            else get_vote_button_style(format_int, len(mogi.players))
        )

        btn = Button(
            label=_display_label(label, mogi),
            style=style,
            custom_id=label.lower().replace(" ", "_"),
        )
        btn.callback = callback
        return btn

    class VoteButtonView(View):
        def __init__(self):
            super().__init__(timeout=None)

    view = VoteButtonView()
    for label in button_labels:
        view.add_item(_build_button(label, is_extra=False))
    for label in extra_buttons:
        view.add_item(_build_button(label, is_extra=True))

    return view


def create_random_teams_vote_view(mogi: Mogi, on_result) -> View:
    """
    Creates a Yes/No view for a secondary Random Teams vote.
    Resolves via on_result(bool) when:
      - yes_votes > 75% of players (True)
      - remaining voters can't push yes past 75% (False)
      - 60-second timeout elapses (True only if >75% already, else False)

    Caller must set view.message after sending so the buttons can be disabled on resolve.
    """
    player_ids = {p.discord_id for p in mogi.players}
    yes_votes: set[int] = set()
    no_votes: set[int] = set()

    class RandomTeamsView(View):
        def __init__(self):
            super().__init__(timeout=60)
            self._resolved = False
            self.message = None

        async def _resolve(self, result: bool):
            if self._resolved:
                return
            self._resolved = True
            for item in self.children:
                item.disabled = True
            if self.message:
                try:
                    await self.message.edit(view=self)
                except Exception:
                    pass
            await on_result(result)

        def _check_early_exit(self):
            if len(yes_votes) > len(player_ids) * threshold:
                return True
            # Even if all remaining vote Yes, can't reach threshold
            if len(player_ids) - len(no_votes) <= len(player_ids) * threshold:
                return False
            return None

        async def on_timeout(self):
            await self._resolve(len(yes_votes) > len(player_ids) * threshold)

    view = RandomTeamsView()

    async def yes_callback(interaction: Interaction):
        if interaction.user.id not in player_ids:
            return await interaction.response.send_message(
                "You're not in this mogi.", ephemeral=True
            )
        await interaction.response.defer(ephemeral=True)
        yes_votes.add(interaction.user.id)
        no_votes.discard(interaction.user.id)
        await interaction.followup.send(
            "Voted **Yes** for Random Teams.", ephemeral=True
        )
        result = view._check_early_exit()
        if result is not None:
            await view._resolve(result)

    async def no_callback(interaction: Interaction):
        if interaction.user.id not in player_ids:
            return await interaction.response.send_message(
                "You're not in this mogi.", ephemeral=True
            )
        await interaction.response.defer(ephemeral=True)
        no_votes.add(interaction.user.id)
        yes_votes.discard(interaction.user.id)
        await interaction.followup.send(
            "Voted **No** for Random Teams.", ephemeral=True
        )
        result = view._check_early_exit()
        if result is not None:
            await view._resolve(result)

    yes_btn = Button(
        label="Yes 🎲",
        style=discord.ButtonStyle.green,
        custom_id="rt_yes",
    )
    yes_btn.callback = yes_callback
    no_btn = Button(
        label="No",
        style=discord.ButtonStyle.red,
        custom_id="rt_no",
    )
    no_btn.callback = no_callback

    view.add_item(yes_btn)
    view.add_item(no_btn)
    return view
