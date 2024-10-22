from discord import slash_command, ApplicationContext
from discord.ext import commands
from utils.commands.button_start import create_button_view
from utils.mogis import get_mogi
from utils.objects import get_inmogi_role
from config import GUILD_IDS

class start(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="start", guild_ids=GUILD_IDS)
    async def start(self, ctx: ApplicationContext):
        mogi = get_mogi(ctx.channel.id)

        # no mogi open
        if not mogi:
            return await ctx.respond("No open mogi in this channel", ephemeral=True)
        # not enough players
        if len(mogi.players) < 5:
            return await ctx.respond("Not enough players to start", ephemeral=True)
        # more than 12 players
        if len(mogi.players) > 12:
            return await ctx.respond("Cant start with more than 12 players")
        # user not in the mogi
        if not await get_inmogi_role() in ctx.author.roles:
            return await ctx.respond("You can't start a mogi you aren't in", ephemeral=True)
        # mogi already started
        if mogi.isPlaying or mogi.isVoting:
            return await ctx.respond("Mogi already started", ephemeral=True)

        mogi.isVoting = True

        global player_count
        player_count = len(self.bot.mogi["players"])
        view = create_button_view(["FFA", "2v2", "3v3", "4v4", "5v5", "6v6"], mogi)
        await ctx.respond(f"Voting start!\n ||{''.join([f'<@{player.discord_id}>' for player in mogi.players])}||", view=view)


def setup(bot: commands.Bot):
    bot.add_cog(start(bot))
