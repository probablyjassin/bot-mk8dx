from discord import SlashCommandGroup

start = SlashCommandGroup(
    name="start", description="Start a mogi. Start voting or force (for mogi managers)."
)

manage = SlashCommandGroup(
    "manage", "Commands for mogi managers to manage players and such."
)

team = SlashCommandGroup(
    name="team", description="Edit Team tags and apply/remove roles"
)

replacement = manage.create_subgroup(
    "replacement", "Substitute a player who can't play anymore."
)

points = SlashCommandGroup(
    name="points", description="Commands for point collection and mmr calculation."
)
