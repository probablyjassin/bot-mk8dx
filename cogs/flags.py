from discord import slash_command, Interaction, Embed, ButtonStyle, Color
from discord.ext import commands
from discord.ui import View, Button

from config import FLAGS

class FlagButton(Button):
    def __init__(self, flag_name: str, is_enabled: bool):
        super().__init__(
            style=ButtonStyle.green if is_enabled else ButtonStyle.red,
            label=f"{flag_name}: {'ON' if is_enabled else 'OFF'}",
            custom_id=f"flag_{flag_name}",
        )
        self.flag_name = flag_name

    async def callback(self, interaction: Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You don't have permission to toggle flags!", ephemeral=True
            )
            return

        cog = interaction.client.get_cog("flags")
        cog.debug_flags[self.flag_name] = not cog.debug_flags[self.flag_name]

        # Update button appearance
        self.style = (
            ButtonStyle.green if cog.debug_flags[self.flag_name] else ButtonStyle.red
        )
        self.label = (
            f"{self.flag_name}: {'ON' if cog.debug_flags[self.flag_name] else 'OFF'}"
        )

        # Update embed
        embed = Embed(title="Debug/Feature Flags", color=Color.blue())
        for flag, value in cog.debug_flags.items():
            embed.add_field(
                name=flag, value="✅ ON" if value else "❌ OFF", inline=True
            )

        await interaction.response.edit_message(
            embed=embed, view=FlagsView(cog.debug_flags)
        )


class FlagsView(View):
    def __init__(self, flags_dict: dict):
        super().__init__(timeout=None)
        for flag_name, flag_value in flags_dict.items():
            self.add_item(FlagButton(flag_name, flag_value))


class flags(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.debug_flags = FLAGS

    @slash_command(name="flags", description="View and toggle bot flags")
    async def show_flags(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(
                "You don't have permission to view flags!", ephemeral=True
            )
            return

        embed = Embed(title="Bot Flags", color=Color.blue())
        for flag, value in self.debug_flags.items():
            embed.add_field(
                name=flag, value="✅ ON" if value else "❌ OFF", inline=True
            )

        await ctx.respond(embed=embed, view=FlagsView(self.debug_flags))


def setup(bot: commands.Bot):
    bot.add_cog(flags(bot))
