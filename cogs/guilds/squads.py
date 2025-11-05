from discord import SlashCommandGroup
from discord.ext import commands

from models import MogiApplicationContext
from utils.data import guild_manager
from utils.decorators import with_player, with_guild


class squads(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    squads = SlashCommandGroup(name="squads")

    @squads.command(
        name="queue",
        description="Mark yourself as available for a guild mogi",
    )
    @with_guild()
    async def queue(self, ctx: MogiApplicationContext):
        queue = guild_manager.read_queue()
        if any(ctx.user.id in arr for arr in queue):
            return await ctx.respond("Already queued up for the guild mogi.")

        guild_manager.queue_up(ctx.lounge_guild, ctx.user.id)
        return await ctx.respond(
            f"<@{ctx.user.id}> queued up for {ctx.lounge_guild.name}!"
        )

    @squads.command(
        name="drop",
        description="Drop from the guild mogi queue",
    )
    @with_guild()
    async def drop(self, ctx: MogiApplicationContext):
        queue = guild_manager.read_queue()
        if not any(ctx.user.id in arr for arr in queue.values()):
            return await ctx.respond("Not queued up for the guild mogi.")

        guild_manager.queue_up(ctx.lounge_guild, ctx.user.id)
        return await ctx.respond(
            f"<@{ctx.user.id}> dropped from the queue for **{ctx.lounge_guild.name}**!"
        )

    @squads.command(
        name="list",
        description="Show the current guild mogi queue",
    )
    async def list(self, ctx: MogiApplicationContext):
        queue = guild_manager.read_queue()
        if not any(arr for arr in queue):
            return await ctx.respond("No players in the current guild mogi queue.")

        queue_str = ""
        for guild_name in queue.keys():
            queue_str += f"### {guild_name}\n"
            for player_id in queue[guild_name]:
                queue_str += f"- <@{player_id}>\n"
            queue_str += "\n"
        return await ctx.respond(queue_str)


def setup(bot: commands.Bot):
    bot.add_cog(squads(bot))
