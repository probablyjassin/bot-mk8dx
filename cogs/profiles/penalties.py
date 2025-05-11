from discord import slash_command, Embed, Option, AllowedMentions
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from models.PlayerModel import PlayerProfile

from utils.data.mogi_manager import mogi_manager
from utils.command_helpers.find_player import search_player
from utils.decorators.checks import is_mogi_manager


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

        if not player_profile:
            return await ctx.respond("Couldn't find that player")

        if not penalty_holder:
            return await ctx.respond("Couldn't find mrboost")

        # Check if player is in a mogi in another channel
        for mogi in mogi_manager.mogi_registry.values():
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
        penalty_holder.mmr = penalty_holder.mmr + abs(mmr)

        await ctx.respond(
            f"Collected penalties from <@{player_profile.discord_id}>",
            allowed_mentions=AllowedMentions.none(),
        )


def setup(bot: commands.Bot):
    bot.add_cog(penalties(bot))
