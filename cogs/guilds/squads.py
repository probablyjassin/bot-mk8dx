from discord import SlashCommandGroup, AllowedMentions
from discord.ext import commands

from models import MogiApplicationContext
from utils.data import guild_manager
from utils.decorators import with_guild, is_mogi_manager


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
        if ctx.user.id in [
            player_id for players in queue.values() for player_id in players
        ]:
            return await ctx.respond("Already queued up for the guild mogi.")

        guild_manager.queue_up(ctx.lounge_guild, ctx.user.id)
        return await ctx.respond(
            f"<@{ctx.user.id}> queued up for **{ctx.lounge_guild.name}**!"
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

        guild_manager.queue_drop(ctx.user.id)
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
            queue_str += f"## {guild_name}\n"
            for player_id in queue[guild_name]:
                queue_str += f"- <@{player_id}>\n"
            queue_str += "\n"
        return await ctx.respond(queue_str)

    @squads.command(name="start", description="Announce the start of a guild mogi.")
    async def start(self, ctx: MogiApplicationContext):
        await ctx.response.defer()

        queue = guild_manager.read_queue()
        valid_guilds: list[str] = []
        min_players = 12
        for guild_name in queue:
            if len(queue[guild_name]) < 2:
                continue
            valid_guilds.append(guild_name)
            min_players = min(min_players, len(queue[guild_name]))

        if len(valid_guilds) < 2:
            return await ctx.respond("Not enough Guilds with enough players!")

        message = f"# Guild Mogi: {min_players}"
        message += f"v{min_players}" * (len(valid_guilds) - 1)
        message += "\n\n"
        for name in valid_guilds:
            message += f"**{name}**\n"
            for player_id in queue[name]:
                message += f"<@{player_id}>\n"
            if subs := len(queue[name]) - min_players:
                message += f"*({subs} subs)*\n"
            message += "\n"
        await ctx.respond(message)

    @squads.command(name="clear", description="Kick everyone from the queue")
    @is_mogi_manager()
    async def clear(self, ctx: MogiApplicationContext):
        guild_manager.write_registry({})
        await ctx.respond("## Guild mogi queue has been emptied!")


def setup(bot: commands.Bot):
    bot.add_cog(squads(bot))
