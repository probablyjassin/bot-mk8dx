from discord import slash_command, ApplicationContext
from discord.ext import commands
from utils.mogis import get_mogi
from utils.mogis import destroy_mogi
from utils.commands.confirm import confirmation

class close_mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    

    @slash_command(name="close", description="Open a mogi")
    async def close(self, ctx: ApplicationContext):
        await ctx.interaction.response.defer()

        mogi = get_mogi(ctx.channel.id)
        if not mogi:
            return await ctx.respond("No open Mogi in this channel.")
        if mogi.isVoting or (mogi.isPlaying and not mogi.isFinished):
            return await ctx.respond("You can't close the Mogi while it's in progress.")

        close_confirm_message = "{} don't close the mogi unless it fully finished. \nClosing will remove all players and discard any points.\n **Are you sure?**".format(ctx.author.mention)
        
        if (await confirmation(ctx, close_confirm_message)):
            destroy_mogi(ctx.channel.id)
            return await ctx.respond("# This channel's Mogi has been closed.")
        await ctx.respond("Cancelled.")

def setup(bot: commands.Bot):
    bot.add_cog(close_mogi(bot))
