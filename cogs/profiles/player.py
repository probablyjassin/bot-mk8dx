from datetime import datetime
import discord
from discord import slash_command, ApplicationContext, Option
from discord.ext import commands
from discord.ui import View, Button
from utils.models import PlayerProfile
from utils.database import db_players, Int64

class player(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="player", description="Show a player and their stats")
    async def player(
        self,
        ctx: ApplicationContext,
        searched_name: str = Option(str, description="defaults to yourself: username | @ mention | discord_id", required=False),
    ):
        potential_player: PlayerProfile = None

        if not searched_name:
            potential_player: PlayerProfile = db_players.find_one({"discord_id": Int64(ctx.author.id)})

        else:
            potential_player: PlayerProfile = db_players.find_one({
                "$or": [{"name": searched_name}, {"discord_id": Int64(searched_name.strip("<@!>"))}]
            })

        if not potential_player:
            return await ctx.respond("Couldn't find that player")
        
        player: PlayerProfile = potential_player
        
        class PlayerView(View):
            def __init__(self, username: str):
                super().__init__(timeout=None)
                self.add_item(
                    Button(
                        label="View on Website", 
                        style=discord.ButtonStyle.link, 
                        url=f"https://mk8dx-yuzu.github.io/{username}"
                    )
                )

        embed = discord.Embed(
            title=f"{searched_name}",
            description="",
            color=discord.Colour.blurple(),
        )
        embed.add_field(name="Discord", value=f"<@{player['discord']}>")

        if player.get("joined"):
            embed.add_field(name="Joined", value=f"{datetime.datetime.fromtimestamp(player['joined']).strftime('%b %d %Y')}")

        rank = calcRank(player["mmr"])
        embed.add_field(name="Rank", value=f"{rank}")
        
        embed.add_field(name="Wins", value=f"{str(player['wins'])}")
        embed.add_field(name="Losses", value=f"{player['losses']}")

        embed.add_field(
            name="Winrate",
            value=f"{round(((player['wins']/(player['wins']+player['losses']) if (player['wins']+player['losses']) else 0)*100))}%",
        )

        embed.add_field(name="MMR", value=f"{player['mmr']}")
        if player['history']:
            embed.add_field(name="History (last 5)", value=f"{', '.join(map(str, player['history'][len(player['history'])-5:]))}")

        if player.get("inactive"):
            embed.add_field(name="Inactive", value="Account marked for inactivity")

        if player.get("dc"):
            embed.add_field(name="DCd", value=f"{player['dc']} times")

        embed.set_author(
            name="Yuzu-Lounge",
            icon_url="https://raw.githubusercontent.com/mk8dx-yuzu/mk8dx-yuzu.github.io/main/public/favicon/android-icon-192x192.png",
        )
        rank.lower()
        embed.set_thumbnail(
            url=f"https://raw.githubusercontent.com/mk8dx-yuzu/mk8dx-yuzu.github.io/main/public/images/ranks/{rank.lower()}.webp"
        )

        await ctx.respond(f"# {searched_name} - overview", embed=embed, view=MyView(searched_name))


def setup(bot: commands.Bot):
    bot.add_cog(player(bot))
