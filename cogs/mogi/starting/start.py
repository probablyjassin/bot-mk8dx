from discord import slash_command, SlashCommandGroup, Option, ApplicationContext
from discord.utils import get
from discord.ext import commands

from utils.command_helpers.btn_factory import create_button_view
from utils.data.mogi_manager import get_mogi

from config import GUILD_IDS


class start(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.MAIN_GUILD = get(self.bot.guilds, id=GUILD_IDS[0])
        self.INMOGI_ROLE = get(self.MAIN_GUILD.roles, name="InMogi")

    start = SlashCommandGroup(name="start", description="Start a mogi")

    @start.command(name="vote", guild_ids=GUILD_IDS)
    async def vote(self, ctx: ApplicationContext):
        mogi = get_mogi(ctx.channel.id)

        # no mogi open
        if not mogi:
            return await ctx.respond("No open mogi in this channel", ephemeral=True)
        # not enough players
        if len(mogi.players) < 0:  # DEBUG: remember to change this in production
            return await ctx.respond("Not enough players to start", ephemeral=True)
        # more than 12 players
        if len(mogi.players) > 12:
            return await ctx.respond("Cant start with more than 12 players")
        # user not in the mogi
        if not self.INMOGI_ROLE in ctx.user.roles:
            return await ctx.respond(
                "You can't start a mogi you aren't in", ephemeral=True
            )
        # mogi already started
        if mogi.isPlaying or mogi.isVoting:
            return await ctx.respond("Mogi already started", ephemeral=True)

        mogi.isVoting = True

        view = create_button_view(["FFA", "2v2", "3v3", "4v4", "6v6"], mogi)
        await ctx.respond(
            f"Voting start!\n ||{''.join([f'<@{player.discord_id}>' for player in mogi.players])}||",
            view=view,
        )

    @start.command(name="force", guild_ids=GUILD_IDS)
    async def force(
        self,
        ctx: ApplicationContext,
        format: str = Option(str, choices=["FFA", "2v2", "3v3", "4v4", "6v6"]),
    ):
        mogi = get_mogi(ctx.channel.id)

        # no mogi open
        if not mogi:
            return await ctx.respond("No open mogi in this channel", ephemeral=True)
        # mogi already started
        if mogi.isPlaying or mogi.isVoting:
            return await ctx.respond("Mogi already started", ephemeral=True)

        mogi.play(int(format[0]) if format[0].isnumeric() else 1)

        lineup = ""
        for i, team in enumerate(mogi.teams):
            lineup += (
                f"{i}. {', '.join([f'<@{player.discord_id}>' for player in team])}\n"
            )

        await ctx.respond(f"Mogi started!\n{lineup}")


def setup(bot: commands.Bot):
    bot.add_cog(start(bot))
