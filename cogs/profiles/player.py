from datetime import datetime
import discord
from discord import slash_command, ApplicationContext, Option
from discord.ext import commands
from discord.ui import View, Button
from models.RankModel import Rank
from models.PlayerModel import PlayerProfile
from utils.data.database import db_players
from utils.maths.ranks import getRankByMMR
from bson.int64 import Int64

class player(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="player", description="Show a player and their stats")
    async def player(
        self,
        ctx: ApplicationContext,
        searched_name: str = Option(str, description="defaults to yourself: username | @ mention | discord_id", required=False),
    ):
        potential_player = None

        if not searched_name:
            potential_player = db_players.find_one({"discord_id": Int64(ctx.author.id)})

        else:
            potential_player = db_players.find_one({
                "$or": [
                    {"name": searched_name}, 
                    {
                        "discord_id": 
                            Int64(searched_name.strip("<@!>")) 
                            if searched_name.strip("<@!>").isdigit() 
                            else None
                    }
                ]
            })

        if not potential_player:
            return await ctx.respond("Couldn't find that player")
        
        player: PlayerProfile = PlayerProfile(**potential_player)

        class PlayerView(View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(
                    Button(
                        label="View on Website", 
                        style=discord.ButtonStyle.link, 
                        url=f"https://mk8dx-yuzu.github.io/{player.name}"
                    )
                )

        embed = discord.Embed(
            title=f"{player.name}",
            description="",
            color=discord.Colour.blurple(),
        )
        embed.add_field(name="Discord", value=f"<@{player.discord_id}>")

        if getattr(player, "joined", None):
            embed.add_field(name="Joined", value=f"{datetime.fromtimestamp(player.joined).strftime('%b %d %Y')}")

        player_rank: Rank = getRankByMMR(player.mmr)
        embed.add_field(name="Rank", value=f"{player_rank.name}")

        player_wins = len([delta for delta in player.history if delta >= 0])
        player_losses = len([delta for delta in player.history if delta < 0])
        embed.add_field(name="Wins", value = player_wins)
        embed.add_field(name="Losses", value = player_losses)

        embed.add_field(
            name="Winrate",
            value=
            str(
                round(
                    ( (player_wins / (player_wins + player_losses) if (player_wins + player_losses) else 0) *100 ) 
                )
            ) + "%"
        )

        embed.add_field(name="MMR", value=f"{player.mmr}")

        if getattr(player, "history", None):
            embed.add_field(name="History (last 5)", value=f"{', '.join(map(str, player.history[ len(player.history) -5: ]))}")

        if getattr(player, "inactive", None):
            embed.add_field(name="Inactive", value="Account marked for inactivity")

        if getattr(player, "disconnects", None):
            embed.add_field(name="DCd", value=f"{player.disconnects} times")

        embed.set_author(
            name="Yuzu-Lounge",
            icon_url="https://raw.githubusercontent.com/mk8dx-yuzu/mk8dx-yuzu.github.io/main/public/favicon/android-icon-192x192.png",
        )

        embed.set_thumbnail(
            url=f"https://raw.githubusercontent.com/mk8dx-yuzu/mk8dx-yuzu.github.io/main/public/images/ranks/{player_rank.name.lower()}.webp"
        )

        await ctx.respond(f"# {player.name} - overview", embed=embed, view=PlayerView())


def setup(bot: commands.Bot):
    bot.add_cog(player(bot))
