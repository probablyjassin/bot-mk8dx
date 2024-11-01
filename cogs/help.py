from discord import slash_command, ApplicationContext, Color
from discord.ext import commands
from utils.command_helpers.info_embed_factory import create_embed

help_fields = {
    "`/join`": "Join an open or unlocked mogi in the current channel.",
    "`/leave`": "Leave a mogi you have joined.",
    "`/l`": "List all players in the current mogi",
    "`/teams`": "List all teams in the current mogi",
    "`/player`": "View your or someone else's summarized stats",
    "These apply to the current channel only:": "",
    "`/open`": "Open a mogi in the current channel",
    "`/close`": "Close a mogi in the current channel",
    "`/start`": "Start a mogi in the current channel",
    "`/stop`": "Stop a mogi in the current channel",
}


class help(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="help", description="A summary of most of the commands to help")
    async def help(self, ctx: ApplicationContext):
        embed = create_embed(
            "Help",
            "Here you can find a brief summary of common commands.",
            "https://raw.githubusercontent.com/mk8dx-yuzu/mk8dx-yuzu.github.io/main/public/favicon/ms-icon-310x310.png",
            help_fields,
            {
                "text": "Yuzu Online",
                "icon_url": "https://images-ext-1.discordapp.net/external/ymL8nMKRGEJwQZNCLRuCAbeHxt3n3HYA0XTD-JUW4m4/https/cdn.discordapp.com/icons/1084911987626094654/a_f51d88cf4421676675437f9cf4fbbff6.gif",
            },
            color=Color.blue(),
            inline=False,
        )

        # TODO: Make the footer image and text take the guild's icon and name instead of hard coded values ↑
        await ctx.respond(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(help(bot))
