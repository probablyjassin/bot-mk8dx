import discord
from discord import ApplicationContext, DiscordException
from discord.ext import commands
from config import ERROR_CHANNEL_ID
from logger import setup_logger

error_logger = setup_logger(__name__, 'error.log')

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: ApplicationContext, error: DiscordException):
        print(f"An error occurred in {ctx.channel.name} by {ctx.author.display_name}")
        error_logger.error(f"An error occurred in {ctx.channel.name} by {ctx.author.display_name}", exc_info=error)

        channel = await self.bot.fetch_channel(ERROR_CHANNEL_ID)
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

    @commands.Cog.listener()
    async def on_command_error(self, ctx: ApplicationContext, error: commands.CommandError):
        if isinstance(error, commands.CommandInvokeError) and isinstance(error.original, discord.errors.InteractionResponded):
            print(f"Interaction already responded in {ctx.channel.name} by {ctx.author.display_name}")
            error_logger.warning(f"Interaction already responded in {ctx.channel.name} by {ctx.author.display_name}", exc_info=error)

            channel = await self.bot.fetch_channel(ERROR_CHANNEL_ID)
            if channel:
                embed = discord.Embed(
                    title="Warning",
                    description=f"Interaction already responded in {ctx.channel.mention} by {ctx.author.mention}",
                    color=discord.Color.orange()
                )
                embed.add_field(name="Command", value=ctx.command)
                embed.add_field(name="Error", value="Interaction already responded")
                await channel.send(embed=embed)
                
    # TODO: Actually test this:
    @commands.Cog.listener()
    async def on_interaction_error(self, interaction: discord.Interaction, error: DiscordException):
        print(f"An error occurred during interaction in {interaction.channel.name} by {interaction.user.display_name}")
        error_logger.error(f"An error occurred during interaction in {interaction.channel.name} by {interaction.user.display_name}", exc_info=error)

        channel = await self.bot.fetch_channel(ERROR_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred during interaction in {interaction.channel.mention} by {interaction.user.mention}",
                color=discord.Color.red()
            )
            embed.add_field(name="Interaction", value=interaction.type)
            embed.add_field(name="Error", value=str(error))
            await channel.send(embed=embed)

        if interaction.response.is_done():
            await interaction.followup.send("An error occurred. The administrators have been notified.", ephemeral=True)
        else:
            await interaction.response.send_message("An error occurred. The administrators have been notified.", ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))