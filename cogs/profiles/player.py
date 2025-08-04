from discord import slash_command, Option, ButtonStyle, Embed, Colour, Member
from discord.ui import View, Button
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from models.RankModel import Rank
from models.PlayerModel import PlayerProfile
from utils.data.data_manager import data_manager, archive_type

from datetime import datetime
from bson.int64 import Int64


class player(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="player", description="Show a player and their stats")
    async def player(
        self,
        ctx: MogiApplicationContext,
        searched_name: str = Option(
            str,
            name="name",
            description="defaults to yourself: username | @ mention | discord_id",
            required=False,
        ),
    ):
        player: PlayerProfile = data_manager.find_player(
            searched_name or Int64(ctx.author.id), archive=archive_type.INCLUDE
        )

        if not player:
            return await ctx.respond("Couldn't find that player")

        class PlayerView(View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(
                    Button(
                        label="View on Website",
                        style=ButtonStyle.link,
                        url=f"https://mk8dx-yuzu.github.io/{player.name}",
                    )
                )

        embed = Embed(
            title=f"{player.name}",
            description="",
            color=Colour.blurple(),
        )
        embed.add_field(name="Discord", value=f"<@{player.discord_id}>")

        if getattr(player, "joined", None):
            embed.add_field(
                name="Joined",
                value=f"{datetime.fromtimestamp(player.joined).strftime('%b %d %Y')}",
            )

        player_rank: Rank = Rank.getRankByMMR(player.mmr)
        embed.add_field(name="Rank", value=player_rank.rankname)

        player_wins = len([delta for delta in player.history if delta >= 0])
        player_losses = len([delta for delta in player.history if delta < 0])
        embed.add_field(name="Wins", value=player_wins)
        embed.add_field(name="Losses", value=player_losses)

        embed.add_field(
            name="Winrate",
            value=str(
                round(
                    (
                        (
                            player_wins / (player_wins + player_losses)
                            if (player_wins + player_losses)
                            else 0
                        )
                        * 100
                    )
                )
            )
            + "%",
        )

        embed.add_field(name="MMR", value=f"{player.mmr}")

        if getattr(player, "history", None):
            embed.add_field(
                name="History (last 5)",
                value=", ".join(map(str, player.history[-5:])),
            )

        if getattr(player, "formats", None):
            most_p_format: str = max(player.formats, key=player.formats.get)
            name = "Mini Mogi (FFA)"
            if most_p_format == "1":
                name = "FFA"
            elif int(most_p_format) >= 2:
                name = f"{most_p_format}v{most_p_format}"
            embed.add_field(
                name="Most played Format",
                value=name if max(player.formats.values()) > 0 else "None played yet",
            )

        if getattr(player, "inactive", None):
            embed.add_field(name="Archived", value="Account is not active")

        if getattr(player, "suspended", None):
            embed.add_field(name="Suspended", value="Account suspended from Lounge")

        if getattr(player, "disconnects", None):
            embed.add_field(name="DCd", value=f"{player.disconnects} times")

        embed.set_author(
            name="Yuzu-Lounge",
            icon_url="https://raw.githubusercontent.com/mk8dx-yuzu/mk8dx-yuzu.github.io/main/public/images/kawaii_icon_by_kevnkkm.png",
        )

        embed.set_thumbnail(
            url=f"https://raw.githubusercontent.com/mk8dx-yuzu/ranks/refs/heads/main/{player_rank.rankname}.png"
        )

        await ctx.respond(f"# {player.name} - overview", embed=embed, view=PlayerView())


def setup(bot: commands.Bot):
    bot.add_cog(player(bot))
