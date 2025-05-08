from discord import slash_command, Interaction, Embed, ButtonStyle, Color
from discord.ext import commands
from discord.ui import View, Button


class flags(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Define your debug flags here. You can add more as needed.
        self.debug_flags = {
            "test1": False,
            "test2": False,
            "test3": False,
        }

    """ @slash_command(name="flags", description="Manage debug flags")
    async def flags(self, interaction: Interaction):
        """Displays and allows toggling of debug flags."""
        embed = Embed(title="Debug Flags", color=Color.blue())

        for flag, state in self.debug_flags.items():
            embed.add_field(
                name=flag, value="Enabled" if state else "Disabled", inline=True
            )

        # Create buttons for each flag
        view = FlagButtons(self.debug_flags, self)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    def toggle_flag(self, flag_name: str):
        """Toggles the state of a specific flag."""
        if flag_name in self.debug_flags:
            self.debug_flags[flag_name] = not self.debug_flags[flag_name]
            return True
        return False


class FlagButtons(View):
    def __init__(self, flags: dict, cog: flags):
        super().__init__(timeout=180)  # Set a timeout for the view
        self.flags = flags
        self.cog = cog
        self.add_flag_buttons()

    def add_flag_buttons(self):
        """Adds a button for each flag."""
        for flag_name in self.flags:
            button = Button(label=f"Toggle {flag_name}", style=ButtonStyle.secondary)
            button.custom_id = f"toggle_flag_{flag_name}"
            button.callback = self.button_callback
            self.add_item(button)

    async def button_callback(self, interaction: Interaction):
        """Handles button clicks to toggle flags."""
        custom_id = interaction.data["custom_id"]
        flag_name = custom_id.replace("toggle_flag_", "")

        if self.cog.toggle_flag(flag_name):
            await interaction.response.defer()  # Defer the interaction update

            # Update the original message with the new flag states
            embed = Embed(title="Debug Flags", color=Color.blue())
            for flag, state in self.cog.debug_flags.items():
                embed.add_field(
                    name=flag, value="Enabled" if state else "Disabled", inline=True
                )

            await interaction.message.edit(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Error toggling flag.", ephemeral=True
            )

    async def on_timeout(self):
        """Disables buttons when the view times out."""
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(view=self) """


async def setup(bot: commands.Bot):
    await bot.add_cog(flags(bot))
