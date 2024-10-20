import discord
from discord import ApplicationContext, DiscordException
from discord.ext import commands
from config import ERROR_CHANNEL

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: ApplicationContext, error: DiscordException):
        print(f"An error occurred in {ctx.channel.name} by {ctx.author.display_name}")
        channel = await self.bot.fetch_channel(ERROR_CHANNEL)
        print(channel)
        if channel:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred in {ctx.channel.mention} by {ctx.author.mention}",
                color=discord.Color.red()
            )
            embed.add_field(name="Command", value=ctx.command)
            embed.add_field(name="Error", value=str(error))
            await channel.send(embed=embed)

        await ctx.respond("An error occurred. The administrators have been notified.")

def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))