from discord import SlashCommandGroup, ApplicationContext
from discord.ext import commands
from utils.mogis import mogi_registry

class debugging(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    debug = SlashCommandGroup(name="debug", description="Debugging commands")

    @debug.command(name="current_mogi", description="print the mogi for this channel")
    async def current_mogi(self, ctx: ApplicationContext):
        mogi = mogi_registry.get(ctx.channel.id)
        await ctx.respond(f"Current Mogi: \n{mogi}")

    @debug.command(name="all_mogis", description="print the mogi registry")
    async def all_mogis(self, ctx: ApplicationContext):
        await ctx.respond(f"Mogi Registry: \n{mogi_registry}")

    @debug.command(name="throw_error", description="throw an error")
    async def throw_error(self, ctx: ApplicationContext):
        raise Exception("This is a test error")

def setup(bot: commands.Bot):
    bot.add_cog(debugging(bot))
