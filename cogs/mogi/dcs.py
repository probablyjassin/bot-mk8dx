from discord import Message, Interaction, Role, AllowedMentions
from discord.ui import View, Button
from discord.utils import get
from discord.ext import commands

from utils.data.mogi_manager import mogi_manager
from models.MogiModel import Mogi

from config import GUILD_IDS


class dcs(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        # if the message pings InMogi and contains "dc"
        if not (
            get(message.role_mentions, name="InMogi")
            and "dc" in message.content.lower()
        ):
            return

        # if the message is in a channel with an open Mogi that is playing
        mogi: Mogi = mogi_manager.get_mogi(message.channel.id)
        if not mogi or not mogi.isPlaying:
            return

        # grab inmogi role
        inmogi_role: Role = get(
            get(self.bot.guilds, id=GUILD_IDS[0]).roles, name="InMogi"
        )

        # callback if player DCd
        async def yes_button_callback(interaction: Interaction):
            if interaction.user.id != message.author.id:
                return await interaction.response.send_message(
                    content="This is not for you",
                    ephemeral=True,
                )
            player.add_disconnect()
            await interaction.response.send_message(
                content=f"<@{player.discord_id}> DCd {inmogi_role.mention}! \nAdded to counter (now {player.disconnects})",
                view=None,
                allowed_mentions=AllowedMentions(roles=True),
            )

        # callback if player did not DC
        async def no_button_callback(interaction: Interaction):
            if interaction.user.id != message.author.id:
                return await interaction.response.send_message(
                    content="This is not for you",
                    ephemeral=True,
                )
            await question.delete()

        # ask the player if they DCd
        if player := next(
            (p for p in mogi.players if p.discord_id == message.author.id), None
        ):
            view = View()
            yes_button = Button(
                label="Yes",
                custom_id="y",
            )
            no_button = Button(
                label="No",
                custom_id="n",
            )
            yes_button.callback = yes_button_callback
            no_button.callback = no_button_callback
            view.add_item(yes_button)
            view.add_item(no_button)
            question = await message.channel.send(
                content=f"Did you DC? <@{message.author.id}>",
                view=view,
            )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(dcs(bot))
