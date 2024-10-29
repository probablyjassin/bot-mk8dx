from discord import slash_command, ApplicationContext, Message, TextChannel
from discord.utils import get
from discord.ext import commands

from utils.command_helpers.btn_factory import create_button_view
from utils.command_helpers.checks import is_mogi_open, is_mogi_in_progress
from utils.data.mogi_manager import mogi_manager

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
        mogi = mogi_manager.get_mogi(ctx.channel.id)

        # user not in the mogi
        if not self.INMOGI_ROLE in ctx.user.roles:
            return await ctx.respond(
                "You can't stop a mogi you aren't in", ephemeral=True
            )

        mogi.stop()
        if mogi.voting_message_id:
            print(mogi.voting_message_id)
            vote_msg: Message = await ctx.channel.fetch_message(mogi.voting_message_id)
            await vote_msg.delete()
        await ctx.respond("Mogi has been stopped")


def setup(bot: commands.Bot):
    bot.add_cog(stop(bot))
