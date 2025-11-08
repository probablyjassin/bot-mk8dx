from discord import SlashCommandGroup, AllowedMentions
from discord.ext import commands

from models import MogiApplicationContext
from utils.data import guild_manager
from utils.decorators import with_guild, with_player, is_mogi_manager


class squads(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    squads = SlashCommandGroup(name="squads")

    @squads.command(
        name="queue",
        description="Mark yourself as available for a guild mogi",
    )
    @with_player()
    @with_guild()
    async def queue(self, ctx: MogiApplicationContext):
        # if already playing
        if len(guild_manager.playing_guilds):
            if target_guild := [
                guild
                for guild in guild_manager.playing_guilds
                if guild.name == ctx.lounge_guild.name
            ]:
                if not target_guild:
                    return await ctx.respond(
                        "The guild mogi is already going on and your guild is not in."
                    )
                target_guild = target_guild[0]
                target_guild.add_sub(ctx.player)
                return await ctx.respond(
                    "You've queued up as a sub for the ongoing guild mogi for your team."
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
            playing_format = guild_manager.guilds_format

            queue_message = f"# Guild Mogi: {playing_format}"
            queue_message += f"v{playing_format}" * (len(playing_guilds) - 1)
            queue_message += "\n\n"

            for playing_guild in playing_guilds:

                queue_message += f"**{playing_guild.name}**\n"

                for player in playing_guild.playing:
                    queue_message += f"<@{player.discord_id}>\n"

                if len(playing_guild.subs):
                    queue_message += "- *subs:*\n"
                    for sub in playing_guild.subs:
                        queue_message += f"*<@{sub.discord_id}>*\n"

                queue_message += "\n"

        return await ctx.respond(queue_message, allowed_mentions=AllowedMentions.none())

    @squads.command(name="start", description="Announce the start of a guild mogi.")
    async def start(self, ctx: MogiApplicationContext):
        await ctx.response.defer()

        if len(guild_manager.playing_guilds):
            return await ctx.respond("Already started.")

        queue = guild_manager.read_queue()
        if len([lst for lst in list(queue.values()) if len(lst) >= 2]) < 2:
            return await ctx.respond("Not enough Guilds with enough players!")

        min_players, playing_guilds = await guild_manager.start()

        message = f"# Guild Mogi: {min_players}"
        message += f"v{min_players}" * (len(playing_guilds) - 1)
        message += "\n\n"
        for playing_guild in playing_guilds:

            message += f"**{playing_guild.name}**\n"

            for player in playing_guild.playing:
                message += f"<@{player.discord_id}>\n"

            if len(playing_guild.subs):
                message += "- *subs:*\n"
                for sub in playing_guild.subs:
                    message += f"*<@{sub.discord_id}>*\n"

            message += "\n"
        await ctx.respond(message)

    @squads.command(name="stop", description="Go back to gathering")
    async def stop(self, ctx: MogiApplicationContext):
        guild_manager.clear_playing()
        await ctx.respond(
            "## Guild mogi has been stopped! Gathering in progress again!"
        )

    @squads.command(name="clear", description="Kick everyone from the queue")
    @is_mogi_manager()
    async def clear(self, ctx: MogiApplicationContext):
        guild_manager.clear_queue()
        await ctx.respond("## Guild mogi queue has been emptied!")

    @squads.command(
        name="debug",
        description="[DEBUG] Show complete guild_manager state",
    )
    @is_mogi_manager()
    async def debug(self, ctx: MogiApplicationContext):
        import json

        debug_info = "# Guild Manager Debug Info\n\n"

        # Queue state
        queue = guild_manager.read_queue()
        debug_info += "## Queue\n```json\n"
        debug_info += json.dumps(queue, indent=2)
        debug_info += "\n```\n\n"

        # Playing guilds
        playing_guilds = guild_manager.read_playing()
        debug_info += f"## Playing Guilds ({len(playing_guilds)})\n```json\n"
        playing_guilds_data = [
            {
                "name": pg.guild.name if hasattr(pg, "guild") else pg.name,
                "playing_count": len(pg.playing) if hasattr(pg, "playing") else 0,
                "subs_count": len(pg.subs) if hasattr(pg, "subs") else 0,
                "playing_ids": (
                    [p.discord_id for p in pg.playing] if hasattr(pg, "playing") else []
                ),
                "subs_ids": (
                    [p.discord_id for p in pg.subs] if hasattr(pg, "subs") else []
                ),
            }
            for pg in playing_guilds
        ]
        debug_info += json.dumps(playing_guilds_data, indent=2)
        debug_info += "\n```\n\n"

        # Format and other state
        debug_info += "## State Variables\n```\n"
        debug_info += f"guilds_format: {guild_manager.guilds_format}\n"
        debug_info += f"placements: {guild_manager.placements}\n"
        debug_info += f"results: {guild_manager.results}\n"
        debug_info += "```\n\n"

        # Full registry dump
        registry = guild_manager.read_registry()
        debug_info += "## Full Registry\n```json\n"
        registry_serializable = {
            "guilds_format": registry["guilds_format"],
            "placements": registry["placements"],
            "results": registry["results"],
            "playing_guilds_count": len(registry["playing_guilds"]),
        }
        debug_info += json.dumps(registry_serializable, indent=2)
        debug_info += "\n```"

        # Split message if too long (Discord limit: 2000 chars)
        if len(debug_info) > 2000:
            chunks = [debug_info[i : i + 1990] for i in range(0, len(debug_info), 1990)]
            await ctx.respond(chunks[0])
            for chunk in chunks[1:]:
                await ctx.send(chunk)
        else:
            await ctx.respond(debug_info)


def setup(bot: commands.Bot):
    bot.add_cog(squads(bot))
