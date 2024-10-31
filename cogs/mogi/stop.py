from discord import slash_command, Message
from discord.utils import get
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from utils.command_helpers.checks import is_mogi_in_progress

from config import GUILD_IDS


class stop(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.MAIN_GUILD = get(self.bot.guilds, id=GUILD_IDS[0])
        self.INMOGI_ROLE = get(self.MAIN_GUILD.roles, name="InMogi")

    @slash_command(name="stop", description="Halt the current mogi")
    @is_mogi_in_progress()
    async def stop(self, ctx: MogiApplicationContext):

        # user not in the mogi
        if not self.INMOGI_ROLE in ctx.user.roles:
            return await ctx.respond(
                "You can't stop a mogi you aren't in", ephemeral=True
            )

        ctx.mogi.stop()
        if ctx.mogi.voting_message_id:
            vote_msg: Message = await ctx.channel.fetch_message(
                ctx.mogi.voting_message_id
            )
            if vote_msg:
                await vote_msg.delete()
        await ctx.respond("Mogi has been stopped")


def setup(bot: commands.Bot):
    bot.add_cog(stop(bot))
