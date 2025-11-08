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
        if len(guild_manager.playing_guilds):
            return await ctx.respond(
                "Can't join or drop from the queue while already playing."
            )

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
        if len(guild_manager.playing_guilds):
            return await ctx.respond(
                "Can't join or drop from the queue while already playing."
            )

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
        playing_guilds = guild_manager.read_playing()
        queue_message = ""

        if not len(playing_guilds):
            if not any(arr for arr in queue):
                return await ctx.respond("No players in the current guild mogi queue.")

            queue_message = ""
            for guild_name in queue.keys():
                queue_message += f"## {guild_name}\n"
                for player_id in queue[guild_name]:
                    queue_message += f"- <@{player_id}>\n"
                queue_message += "\n"
        else:
            playing_guilds = guild_manager.playing_guilds
            playing_format = guild_manager.guilds_format

            queue_message = f"# Guild Mogi: {playing_format}"
            queue_message += f"v{playing_format}" * (len(playing_guilds) - 1)
            queue_message += "\n\n"
            for name in playing_guilds:
                queue_message += f"**{name}**\n"
                for player_id in queue[name]:
                    queue_message += f"<@{player_id}>\n"
                if subs := len(queue[name]) - playing_format:
                    queue_message += f"*({subs} subs)*\n"
                queue_message += "\n"

        return await ctx.respond(queue_message, allowed_mentions=AllowedMentions.none())

    @squads.command(name="start", description="Announce the start of a guild mogi.")
    async def start(self, ctx: MogiApplicationContext):
        await ctx.response.defer()

        queue = guild_manager.read_queue()
        min_players, valid_guilds = guild_manager.start()

        if len(valid_guilds) < 2:
            guild_manager.clear_playing()
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
        guild_manager.clear_queue()
        await ctx.respond("## Guild mogi queue has been emptied!")


def setup(bot: commands.Bot):
    bot.add_cog(squads(bot))
