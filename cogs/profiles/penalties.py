from discord import slash_command, Embed, Option, AllowedMentions
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from models.PlayerModel import PlayerProfile

from utils.data.mogi_manager import mogi_manager
from utils.command_helpers.find_player import search_player
from utils.command_helpers.checks import is_mogi_manager


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
    @is_mogi_manager()
    async def tax(
        self,
        ctx: MogiApplicationContext,
        player=Option(str, "Player to collect penalties from"),
        mmr=Option(int, "MMR to collect"),
    ):
        player_profile: PlayerProfile = search_player(player)
        penalty_holder: PlayerProfile = search_player(self.bot.user.id)

        for mogi in list(mogi_manager.mogi_registry.values()):
            if player_profile in mogi.players:
                return await ctx.respond(
                    f"Can't change MMR of <@{player_profile.discord_id}> while they are in a mogi",
                    allowed_mentions=AllowedMentions.none(),
                )

        player_profile.mmr = player_profile.mmr - abs(mmr)
        penalty_holder.mmr = penalty_holder.mmr + abs(mmr)

        await ctx.respond(
            f"Collected penalties from <@{player_profile.discord_id}>",
            allowed_mentions=AllowedMentions.none(),
        )


def setup(bot: commands.Bot):
    bot.add_cog(penalties(bot))
