from discord import Member
from discord.utils import get

from models.CustomMogiContext import MogiApplicationContext
from models.MogiModel import Mogi
from models.RankModel import Rank


async def update_roles(
    ctx: MogiApplicationContext,
    mogi: Mogi,
):
    """
    Updates the roles of players in a Mogi based on their MMR changes.
    ### Args:
        ctx (`ApplicationContext`): The context where the command was invoked.
        mogi (`Mogi`): The Mogi instance to perform the action on.
    """
    for player in mogi.players:
        discord_member: Member = get(ctx.guild.members, id=int(player.discord_id))
        if not discord_member:
            await ctx.results_channel.send(
                f"Skipped {player.name}, couldn't find member in server."
            )
            continue

        if player in mogi.subs:
            await ctx.results_channel.send(
                f"Excluded {discord_member.mention} because they subbed"
            )
            continue

        current_rank = Rank.getRankByMMR(player.mmr)
        new_rank = Rank.getRankByMMR(
            player.mmr + mogi.mmr_results_by_group[mogi.players.index(player)]
        )

        if current_rank.rankname != new_rank.rankname:

            await discord_member.remove_roles(
                ctx.get_lounge_role(f"Lounge - {current_rank.rankname}"),
                reason="MMR change",
            )
            await discord_member.add_roles(
                ctx.get_lounge_role(f"Lounge - {new_rank.rankname}"),
                reason="MMR change",
            )

            await ctx.results_channel.send(
                f"{discord_member.mention} is now in {new_rank.rankname}"
            )
