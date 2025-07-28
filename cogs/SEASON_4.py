from discord.ext import commands
from discord.utils import get

from utils.data.data_manager import db_players
from models.CustomMogiContext import MogiApplicationContext
from utils.decorators.checks import is_admin

from models.RankModel import Rank

from discord import slash_command
import json
import discord
from io import StringIO


class season4(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="season4")
    @is_admin()
    async def season4(self, ctx: MogiApplicationContext):
        await ctx.response.defer()

        def reset_mmr_exponential(old_mmr: int) -> int:
            base = 2000
            scaling_factor = 1.2
            exponent = 0.85

            if old_mmr == base:
                return base
            elif old_mmr > base:
                # Compress high MMRs downward
                reduced = base + ((old_mmr - base) * scaling_factor) ** exponent
            else:
                # Pull low MMRs upward with mirrored logic
                reduced = base - ((base - old_mmr) * scaling_factor) ** exponent

            return round(reduced / 5) * 5

        players = db_players.find({})
        all_players: list[dict] = list(players)

        season_3_role = get(ctx.guild.roles, name="Season 3 Player")
        # lounge_player_role = get(ctx.guild.roles, name="Lounge Player")

        rank_names = [rank.rankname for rank in Rank]
        rank_roles = [
            get(ctx.guild.roles, name=f"Lounge - {name}") for name in rank_names
        ]

        updated_players = []
        for i, player in enumerate(all_players):

            if i % 20 == 0:
                await ctx.send(f"Processing player {i}/{len(all_players)}...")

            try:
                player_member = await ctx.guild.fetch_member(player["discord_id"])
            except:
                await ctx.send(
                    f"Skipped <@{player['discord_id']}> who is not on the server anymore."
                )
                continue

            updated_player = player.copy()

            """ # Don't include players who never played
            if len(player["history"]) == 0:
                if lounge_player_role in player_member.roles:
                    player_member.remove_roles(lounge_player_role)
                continue """
            for role in rank_roles:
                if role in player_member.roles:
                    await player_member.remove_roles(role)

            if season_3_role not in player_member.roles:
                await player_member.add_roles(season_3_role, reason="Season 4 Launch")

            old_mmr = player.get("mmr")
            updated_player["mmr"] = reset_mmr_exponential(old_mmr)

            new_rank = Rank.getRankByMMR(updated_player["mmr"]).rankname
            new_rank_role = [role for role in rank_roles if new_rank in role.name][0]
            if new_rank_role not in player_member.roles:
                await player_member.add_roles(new_rank_role)

            updated_player["history"] = []

            if updated_player.get("disconnects"):
                updated_player["disconnects"] = None

            updated_player["formats"] = {str(format): 0 for format in range(7)}

            updated_players.append(updated_player)

        # Create JSON string
        json_data = json.dumps(updated_players, indent=2, default=str)

        # Create file-like object
        json_file = StringIO(json_data)

        # Send as file attachment
        await ctx.followup.send(
            f"Created {len(updated_players)} Season 4 players from {len(all_players)} original players.",
            file=discord.File(json_file, filename="season4_players.json"),
        )


def setup(bot: commands.Bot):
    bot.add_cog(season4(bot))
