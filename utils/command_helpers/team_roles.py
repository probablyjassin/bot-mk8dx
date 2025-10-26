from discord import Interaction
from discord.utils import get

from models.CustomMogiContext import MogiApplicationContext
from models.MogiModel import Mogi


async def apply_team_roles(ctx: MogiApplicationContext | Interaction, mogi: Mogi):
    if mogi.format == 1:
        return

    all_team_roles = [get(ctx.guild.roles, name=f"Team {i+1}") for i in range(5)]
    if len(all_team_roles[0].members) > 0:
        return await ctx.channel.send(
            "Team roles already assigned to some members. Two channel mogis can't have team roles each."
        )

    for i, team in enumerate(mogi.teams):
        for player in team:
            await get(ctx.guild.members, id=player.discord_id).add_roles(
                all_team_roles[i], reason="Team roles applied"
            )
    await ctx.channel.send("Assigned team roles")


async def remove_team_roles(ctx: MogiApplicationContext | Interaction):
    all_team_roles = [get(ctx.guild.roles, name=f"Team {i+1}") for i in range(5)]

    if len(all_team_roles[0].members) == 0:
        return

    for role in all_team_roles:
        for member in role.members:
            await member.remove_roles(role, reason="Team roles removed")

    await ctx.channel.send("Removed team roles")
