from discord import SlashCommandGroup

manage = SlashCommandGroup(
    "manage", "Commands for mogi managers to manage players and such."
)

replacement = manage.create_subgroup(
    "replacement", "Substitute a player who can't play anymore."
)
