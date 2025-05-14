import time
import textwrap

from discord import slash_command
from discord.ext import commands

from models.RoomModel import Room
from models.CustomMogiContext import MogiApplicationContext

from utils.data.roombrowser import get_room_info, ServerType
from utils.command_helpers.info_embed_factory import create_embed


class rooms(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="room", description="Get info on people playing on EU Main")
    async def room(self, ctx: MogiApplicationContext):
        room: Room = get_room_info(ServerType.MAIN)

        if not room:
            return await ctx.respond(
                embed=create_embed(
                    title="Room not found",
                    description="The room browser may be temporarily unavailable.",
                )
            )

        info = {
            "Players": f"{len(room.players)}/{room.maxPlayers}",
        }

        common_game = room.most_popular_game()
        if common_game:
            info[f"{common_game[0]} people are playing"] = common_game[1]

        await ctx.respond(
            embed=create_embed(
                title=room.name,
                description=textwrap.shorten(
                    room.description, width=256, placeholder="..."
                ),
                fields=info,
            )
        )

    @slash_command(name="status", description="Get the status of the current mogi")
    async def status(self, ctx: MogiApplicationContext):
        room: Room = (
            ctx.mogi.room if ctx.mogi.room else get_room_info(ServerType.LOUNGE)
        )

        data = {}

        if not ctx.mogi:
            title = "No mogi"
        elif not ctx.mogi.isPlaying:
            title = f"Gathering: {len(ctx.mogi.players)}"
        else:
            title = f"{len(ctx.mogi.players)} players already playing right now"
            if ctx.mogi.started_at:
                diff_minutes = int((time.time() - ctx.mogi.started_at) / 60)
                title += f"\n{diff_minutes} minutes elapsed"

        if ctx.mogi:
            data["Players"] = f"{len(ctx.mogi.players)}/12"

        data[room.name if room else "Server"] = (
            f"{len(room.players)}/12" if room else "unavailable"
        )

        await ctx.respond(
            embed=create_embed(title=title, description=None, fields=data)
        )


def setup(bot: commands.Bot):
    bot.add_cog(rooms(bot))
