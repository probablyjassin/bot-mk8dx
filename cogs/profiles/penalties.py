from discord import slash_command, Embed, Option, AllowedMentions
from discord.ext import commands

from models import MogiApplicationContext, PlayerProfile

from utils.data import data_manager, mogi_manager
from utils.decorators import is_mogi_manager, with_player


class penalties(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(
        name="bank",
        description="Check MrBoost's bank balance",
    )
    async def bank(self, ctx: MogiApplicationContext):

        player: PlayerProfile = data_manager.Players.find("mrboost")

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
    @with_player(query_varname="player")
    async def tax(
        self,
        ctx: MogiApplicationContext,
        player=Option(str, "Player to collect penalties from"),
        mmr=Option(int, "MMR to collect"),
    ):
        player_profile = ctx.player

        # Check if player is in a mogi in another channel
        for mogi in mogi_manager.read_registry().values():
            if player_profile in mogi.players and mogi.channel_id != ctx.channel.id:
                return await ctx.respond(
                    f"This player is currently in a mogi in <#{mogi.channel_id}>. Use the command there."
                )

        # Use the player profile instance from the mogi the player is in right of (if applicable)
        if ctx.mogi and player_profile in ctx.mogi.players:
            player_profile: PlayerProfile = next(
                (
                    p
                    for p in ctx.mogi.players
                    if p.discord_id == player_profile.discord_id
                ),
                None,
            )

        player_profile.mmr = player_profile.mmr - abs(mmr)

        await ctx.respond(
            f"Collected penalties from <@{player_profile.discord_id}>",
            allowed_mentions=AllowedMentions.none(),
        )


def setup(bot: commands.Bot):
    bot.add_cog(penalties(bot))
