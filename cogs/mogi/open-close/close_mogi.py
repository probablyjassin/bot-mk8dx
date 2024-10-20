from discord import slash_command, ApplicationContext
from discord.ext import commands, tasks
from utils.mogis import close_mogi
from utils.confirm import confirmation

class close_mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="close", description="Open a mogi")
    async def close_mogi(self, ctx: ApplicationContext):
        await ctx.interaction.response.defer()
        
        willClose = await confirmation(ctx, "Are you sure you want to close this mogi?")
        await ctx.respond(willClose)

def setup(bot: commands.Bot):
    bot.add_cog(close_mogi(bot))
