from discord import SlashCommandGroup, Option
from discord.utils import get
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from models.PlayerModel import PlayerProfile

from utils.data.data_manager import data_manager
from utils.decorators.checks import (
    is_mogi_in_progress,
    is_in_mogi,
    is_moderator,
    is_mogi_manager,
)

import re


class team_tags(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    team = SlashCommandGroup(
        name="team", description="Edit Team tags and apply/remove roles"
    )

    @team.command(name="tag", description="set a tag for your own team")
    @is_mogi_in_progress()
    @is_in_mogi()
    async def tag(
        self,
        ctx: MogiApplicationContext,
        tag: str = Option(
            str, name="tag", description="what tag to set for your team", required=True
        ),
    ):
        if ctx.mogi.format == 1:
            return await ctx.respond("This command is not available in FFA mogis.")

        if len(tag) > 40:
            return await ctx.respond("Your team tag must be 40 characters or less")

        urls_pattern = re.compile(r"(https?://[^\s]+)")
        if urls_pattern.search(tag):
            tag = urls_pattern.sub("", tag)

        if not tag:
            return await ctx.respond("Invalid tag")

        for player in ctx.mogi.players:
            if player.name in tag:
                return await ctx.respond(
                    "You cannot include another player's name in your tag."
                )

        player: PlayerProfile = data_manager.find_player(ctx.interaction.user.id)

        team_i = [i for i, subarray in enumerate(ctx.mogi.teams) if player in subarray][
            0
        ]
        ctx.mogi.team_tags[team_i] = tag

        await ctx.respond(f"Team {team_i+1} tag: {tag}", suppress_embeds=True)

    @team.command(name="set", description="set a tag for any team by number")
    @is_mogi_manager()
    @is_mogi_in_progress()
    @is_in_mogi(except_admin=True)
    async def set(
        self,
        ctx: MogiApplicationContext,
        teamnumber: int = Option(
            int, name="teamnumber", description="which team's tag to set"
        ),
        tag: str = Option(str, name="tag", description="which tag to set"),
    ):
        if ctx.mogi.format == 1:
            return await ctx.respond("This command is not available in FFA mogis.")

        ctx.mogi.team_tags[teamnumber - 1] = tag
        await ctx.respond(f"Updated Team {teamnumber}'s tag to {tag}")

    @team.command(name="apply_roles", description="assign team roles")
    @is_mogi_manager()
    @is_mogi_in_progress()
    async def apply_roles(self, ctx: MogiApplicationContext):
        await ctx.defer()

        if ctx.mogi.format == 1:
            return await ctx.respond("This command is not available in FFA mogis.")

        all_team_roles = [get(ctx.guild.roles, name=f"Team {i+1}") for i in range(5)]
        if len(all_team_roles[0].members) > 0:
            return await ctx.respond(
                "Team roles already assigned to some members. Two channel mogis can't have team roles each."
            )

        for i, team in enumerate(ctx.mogi.teams):
            for player in team:
                await get(ctx.guild.members, id=player.discord_id).add_roles(
                    all_team_roles[i], reason="/apply_roles"
                )
        await ctx.respond("Assigned team roles")

    @team.command(name="unapply_roles", description="remove team roles")
    @is_moderator()
    async def unapply_roles(self, ctx: MogiApplicationContext):
        await ctx.defer()

        all_team_roles = [get(ctx.guild.roles, name=f"Team {i+1}") for i in range(5)]

        if len(all_team_roles[0].members) == 0:
            return await ctx.respond("Team roles aren't assigned to anyone.")

        for role in all_team_roles:
            for member in role.members:
                await member.remove_roles(role, reason="/unapply_roles")
        await ctx.respond("Removed team roles")


def setup(bot: commands.Bot):
    bot.add_cog(team_tags(bot))
