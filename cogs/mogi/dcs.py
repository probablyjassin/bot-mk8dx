from discord import Message, Interaction, Role
from discord.ui import View, Button
from discord.utils import get
from discord.ext import commands

from utils.data.mogi_manager import mogi_manager
from models.MogiModel import Mogi
from models.CustomMogiContext import MogiApplicationContext

from config import GUILD_IDS, LOG_CHANNEL_ID


class dcs(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot or message.channel.id != LOG_CHANNEL_ID:
            return

        inmogi_role: Role = get(
            get(self.bot.guilds, id=GUILD_IDS[0]).roles, name="InMogi"
        )

        async def button_callback(interaction: Interaction):
            if interaction.user.id != message.author.id:
                return await interaction.response.send_message(
                    content="This is not for you",
                    ephemeral=True,
                )
            player.add_disconnect()
            await interaction.response.send_message(
                content=f"<@{player.discord_id}> DCd {inmogi_role.mention}! \nAdded to counter (now {player.disconnects})",
                view=None,
            )

        if (
            get(message.role_mentions, name="InMogi")
            and "dc" in message.content.lower()
        ):
            if mogi := mogi_manager.get_mogi(message.channel.id):
                if player := next(
                    (p for p in mogi.players if p.discord_id == message.author.id), None
                ):
                    if mogi.isPlaying and message.channel.id == LOG_CHANNEL_ID:
                        view = View()
                        button = Button(
                            label="Yes",
                            custom_id="y",
                        )
                        button.callback = button_callback
                        view.add_item(button)
                        await message.channel.send(
                            content=f"Did you DC? <@{message.author.id}>",
                            view=view,
                        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(dcs(bot))
