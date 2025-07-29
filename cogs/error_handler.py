from discord import Interaction, DiscordException, errors, Color
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from utils.command_helpers.info_embed_factory import create_embed
from logger import setup_logger

from config import LOG_CHANNEL_ID


error_logger = setup_logger(__name__, "error.log", console=False)

DEFAULT_ERROR_MESSAGE = "An error occurred. The administrators have been notified."


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(
        self, ctx: MogiApplicationContext, error: DiscordException
    ):
        # predicate check failures get handled in the command, ignore them here
        if isinstance(error, errors.CheckFailure):
            return

        # Handle cooldown specifically for /register
        if ctx.command.name == "register":
            if isinstance(error, commands.CommandOnCooldown):
                remaining_time = error.retry_after
                hours = int(remaining_time // 3600)
                minutes = int((remaining_time % 3600) // 60)

                await ctx.respond(
                    f"You have failed to choose the correct option in the selection. Try again after {hours}h {minutes}m and read ⁠ℹ️ competitive and 📕 lounge-rules completely to understand which option is the correct option.",
                    ephemeral=True,
                )
                return

        if isinstance(error, commands.errors.CommandOnCooldown):
            minutes, _ = divmod(error.retry_after, 60)
            minutes = max(1, minutes)
            return await ctx.respond(
                f"This command is on cooldown. Try again in {int(minutes)} minute{'s' if minutes != 1 else ''}."
            )

        # ignore errors in DMs, bot is not meant to be used there
        if not getattr(ctx.channel, "name", False):
            return await ctx.respond("Don't use this bot in DMs")

        # handle every other error
        error_logger.error(
            f"An error occurred in {ctx.channel.name} by {ctx.author.display_name}",
            exc_info=error,
        )
        error_channel = await self.bot.fetch_channel(LOG_CHANNEL_ID)

        if error_channel:
            await error_channel.send(
                embed=create_embed(
                    title="Application Command Error",
                    description=f"An error occurred in {ctx.channel.mention} by {ctx.author.mention}",
                    fields={"Command": ctx.command, "Error": str(error)},
                    color=Color.red(),
                    inline=True,
                )
            )

        await ctx.respond(DEFAULT_ERROR_MESSAGE, ephemeral=True)

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        # ignore command not found errors
        if isinstance(error, commands.errors.CommandNotFound):
            return

    @commands.Cog.listener()
    async def on_interaction_error(
        self, interaction: Interaction, error: DiscordException
    ):

        error_logger.error(
            f"An error occurred during interaction in {interaction.channel.name} by {interaction.user.display_name}",
            exc_info=error,
        )
        error_channel = await self.bot.fetch_channel(LOG_CHANNEL_ID)

        if error_channel:
            await error_channel.send(
                embed=create_embed(
                    title="Interaction Error",
                    description=f"An error occurred during interaction in {interaction.channel.name} by {interaction.user.display_name}",
                    fields={
                        "Type of Interaction": interaction.type,
                        "Error": str(error),
                    },
                    color=Color.red(),
                    inline=True,
                )
            )

        if interaction.response.is_done():
            await interaction.followup.send(DEFAULT_ERROR_MESSAGE, ephemeral=True)
        else:
            await interaction.response.send_message(
                DEFAULT_ERROR_MESSAGE, ephemeral=True
            )


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))
