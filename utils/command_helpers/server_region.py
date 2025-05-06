from discord import Member, Role
from discord.utils import get

from models.RoomModel import Room
from utils.data.mogi_manager import mogi_manager
from models.CustomMogiContext import MogiApplicationContext

from config import ROOMS


def get_best_server(ctx: MogiApplicationContext) -> Room | None:
    REGIONS = ["Europe", "North America", "South America", "Africa", "Asia", "Oceania"]
    REGION_ROLES: list[Role] = [get(ctx.guild.roles, name=region) for region in REGIONS]
    regions_dict: dict[str, int] = {region: 0 for region in REGIONS}

    player_discord_members: list[Member] = [
        get(ctx.guild.members, player.discord_id) for player in ctx.mogi.players
    ]
    for member in player_discord_members:
        for role in REGION_ROLES:
            if role in member.roles:
                regions_dict[role.name] += 1

    max_score = max(regions_dict.values())
    best_region = [
        region for region, score in regions_dict.items() if score == max_score
    ][0]

    available_rooms = ROOMS
    for mogi in mogi_manager.read_registry().values():
        if mogi.room:
            available_rooms.remove(mogi.room)

    room_candidates = [room for room in available_rooms if best_region in room.name]

    return (
        room_candidates[0]
        if room_candidates
        else available_rooms[0] if available_rooms else None
    )
