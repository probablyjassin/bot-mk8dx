from discord import slash_command, SlashCommandGroup, Option, ApplicationContext
from discord.utils import get
from discord.ext import commands

from utils.command_helpers.btn_factory import create_button_view
from utils.command_helpers.checks import is_mogi_open, is_mogi_in_progress
from utils.data.mogi_manager import get_mogi

from config import GUILD_IDS


class stop(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.MAIN_GUILD = get(self.bot.guilds, id=GUILD_IDS[0])
        self.INMOGI_ROLE = get(self.MAIN_GUILD.roles, name="InMogi")

    @slash_command(name="stop", description="Halt the current mogi")
    @is_mogi_open()
    @is_mogi_in_progress()
    async def stop(self, ctx: ApplicationContext):
        mogi = get_mogi(ctx.channel.id)

        # user not in the mogi
        if not self.INMOGI_ROLE in ctx.user.roles:
            return await ctx.respond(
                "You can't stop a mogi you aren't in", ephemeral=True
            )

        mogi.stop()
        await ctx.respond("Mogi has been stopped")


def setup(bot: commands.Bot):
    bot.add_cog(stop(bot))
