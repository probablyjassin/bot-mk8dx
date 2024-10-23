from discord import slash_command, ApplicationContext
from discord.ext import commands
from utils.mogis import get_mogi
from models.MogiModel import Mogi

class leave_mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="l", description="List the players in this mogi")
    async def l(self, ctx: ApplicationContext):
        mogi: Mogi = get_mogi(ctx.channel.id)
        if not mogi:
            return await ctx.respond("There is no mogi open in this channel.")
        if len(mogi.players) == 0:
            return await ctx.respond("No players in this mogi.")
        list_of_players = "\n".join([f"{i+1}. {(await self.bot.fetch_user(player.discord_id)).display_name}" for i, player in enumerate(mogi.players)])
        await ctx.respond(f"Players in this mogi:\n{list_of_players}")

def setup(bot: commands.Bot):
    bot.add_cog(leave_mogi(bot))
