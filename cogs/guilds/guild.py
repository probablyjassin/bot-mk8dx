from datetime import datetime

from discord import slash_command, Option, Embed, ButtonStyle, Colour
from discord.ui import View, Button
from discord.ext import commands

from models import MogiApplicationContext
from utils.command_helpers import guild_name_autocomplete
from utils.decorators import with_guild


class guild(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(
        name="guild",
        description="View your guild or a guild of your choice",
    )
    @with_guild(query_varname="name")
    async def guild(
        self,
        ctx: MogiApplicationContext,
        name=Option(str, "Name", required=False, autocomplete=guild_name_autocomplete),
    ):
        await ctx.defer()

        if not (guild := ctx.lounge_guild):
            return await ctx.respond(
                f"Couldn't find {'that' if name else 'your'} guild."
            )

        class GuildView(View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(
                    Button(
                        label="View on Website",
                        style=ButtonStyle.link,
                        url=f"https://mk8dx-yuzu.github.io/",
                    )
                )

        embed = Embed(
            title=f"{guild.name}",
            description="",
            color=Colour.blurple(),
        )

        if getattr(guild, "player_ids", None):
            member_mentions = "\n".join(
                [
                    f"<@{player_id}>{' ⭐' if i == 0 else ''}"
                    for i, player_id in enumerate(guild.player_ids)
                ]
            )
            embed.add_field(
                name=f"Members ({len(guild.player_ids)})",
                value=member_mentions if member_mentions else "No members",
                inline=False,
            )

        embed.add_field(name="MMR", value=f"{guild.mmr}")

        guild_wins = len([delta for delta in guild.history if delta >= 0])
        guild_losses = len([delta for delta in guild.history if delta < 0])
        embed.add_field(name="Wins", value=guild_wins)
        embed.add_field(name="Losses", value=guild_losses)

        if getattr(guild, "history", None):
            embed.add_field(
                name="History (last 5)",
                value=", ".join(map(str, guild.history[-5:])),
            )

        embed.add_field(
            name="Winrate",
            value=str(
                round(
                    (
                        (
                            guild_wins / (guild_wins + guild_losses)
                            if (guild_wins + guild_losses)
                            else 0
                        )
                        * 100
                    )
                )
            )
            + "%",
        )

        if getattr(guild, "creation_date", None):
            embed.add_field(
                name="Created at",
                value=f"{datetime.fromtimestamp(guild.creation_date).strftime('%b %d %Y')}",
            )

        embed.set_author(
            name="Yuzu-Lounge",
            icon_url="https://raw.githubusercontent.com/mk8dx-yuzu/mk8dx-yuzu.github.io/main/public/images/kawaii_icon_by_kevnkkm.png",
        )
        embed.set_thumbnail(url=guild.icon)

        await ctx.respond(
            f"# {guild.name} - guild overview", embed=embed, view=GuildView()
        )


def setup(bot: commands.Bot):
    bot.add_cog(guild(bot))
