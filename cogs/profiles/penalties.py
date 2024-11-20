from discord import slash_command, Embed, Option
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from models.PlayerModel import PlayerProfile

from utils.command_helpers.find_player import search_player
from utils.command_helpers.checks import is_moderator


class penalties(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(
        name="bank",
        description="Check MrBoost's bank balance",
    )
    async def bank(self, ctx: MogiApplicationContext):

        player: PlayerProfile = search_player("mrboost")

        if not player:
            return await ctx.respond("Couldn't find that player")

        embed: Embed = Embed(title=f"{player.name}")
        embed.add_field(
            name="MMR",
            value=f"{player.mmr}",
            inline=True,
        )
        embed.set_image(
            url="https://raw.githubusercontent.com/mk8dx-yuzu/images/7ff99fd3ac23c74c75fbf964f0d2070342eb33ee/mrboost.gif"
        )

        await ctx.respond(f"mrboost - overview", embed=embed)

    @slash_command(
        name="tax",
        description="Collect MMR for penalties",
    )
    @is_moderator()
    async def tax(
        self,
        ctx: MogiApplicationContext,
        searched_player=Option(str, "Player to collect penalties from"),
        mmr=Option(int, "MMR to collect"),
    ):
        player: PlayerProfile = search_player(searched_player)
        mrboost: PlayerProfile = search_player("mrboost")

        player.mmr = player.mmr - abs(mmr)
        mrboost.mmr = mrboost.mmr + abs(mmr)

        await ctx.respond("Penalties collected")


def setup(bot: commands.Bot):
    bot.add_cog(penalties(bot))
