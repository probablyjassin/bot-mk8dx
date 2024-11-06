from discord import SlashCommandGroup, Option
from discord.utils import get
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from models.PlayerModel import PlayerProfile

from utils.command_helpers.command_groups import team
from utils.command_helpers.find_player import search_player
from utils.command_helpers.checks import is_mogi_in_progress, is_in_mogi


class team_tags(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

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

        player: PlayerProfile = search_player(ctx.interaction.user.id)

        team_i = [i for i, subarray in enumerate(ctx.mogi.teams) if player in subarray][
            0
        ]
        ctx.mogi.team_tags[team_i] = tag

        await ctx.respond(f"Team {team_i+1} tag: {tag}")

    @team.command(name="set", description="set a tag for any team by number")
    @is_mogi_in_progress()
    @is_in_mogi()
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
    @is_mogi_in_progress()
    @is_in_mogi()
    async def apply_roles(self, ctx: MogiApplicationContext):
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
                    all_team_roles[i]
                )
        await ctx.respond("Assigned team roles")

    @team.command(name="unapply_roles", description="remove team roles")
    @is_mogi_in_progress()
    @is_in_mogi()
    async def unapply_roles(self, ctx: MogiApplicationContext):
        all_team_roles = [get(ctx.guild.roles, name=f"Team {i+1}") for i in range(5)]

        if len(all_team_roles[0].members) == 0:
            return await ctx.respond("Team roles aren't assigned to anyone.")

        for role in all_team_roles:
            for member in role.members:
                await member.remove_roles(role)
        await ctx.respond("Removed team roles")


def setup(bot: commands.Bot):
    bot.add_cog(team_tags(bot))
