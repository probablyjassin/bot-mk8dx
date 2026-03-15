"""
Currently unused code that was previously used for picking the server that best fits the region of most players.
Most players are from Europe, so this feature is overkill.
"""

from discord import Member, Role, Interaction
from discord.utils import get

from models.CustomMogiContext import MogiApplicationContext
from models.MogiModel import Mogi
from models.RoomModel import Room
from utils.data.mogi_manager import mogi_manager

from config import ROOMS_CONFIG

ROOMS: list[Room] = [
    Room.from_address(room["address"], room["port"]) for room in ROOMS_CONFIG
]

REGIONS = ["Europe", "North America", "South America", "Africa", "Asia", "Oceania"]


async def get_best_server(
    ctx: Interaction | MogiApplicationContext, mogi: Mogi
) -> Room | None:
    if not ROOMS:
        default_room = ROOMS_CONFIG[0]
        return Room(
            address=default_room["address"],
            description="Join Discord to play here! dsc.gg/yuzuonline",
            externalGuid="yuzuonline",
            hasPassword=True,
            id="yuzuonline",
            maxPlayers=15,
            name="EU MAIN 🌍 | LOUNGE → Join Discord to play here! dsc.gg/yuzuonline",
            netVersion=1,
            owner="yuzuonline",
            players=[],
            port=4600,
            preferredGameName="Mario Kart 8 Deluxe",
            preferredGameId=1,
        )

    REGION_ROLES: list[Role] = [get(ctx.guild.roles, name=region) for region in REGIONS]
    regions_dict: dict[str, int] = {region: 0 for region in REGIONS}

    players = mogi.players if mogi else []

    player_discord_members: list[Member] = [
        get(ctx.guild.members, id=player.discord_id) for player in players
    ]
    for member in player_discord_members:
        for role in REGION_ROLES:
            if role in member.roles:
                regions_dict[role.name] += 1

    max_score = max(regions_dict.values())
    best_region = [
        region for region, score in regions_dict.items() if score == max_score
    ][0]

    region_to_server = {
        "Europe": "EU",
        "North America": "NA",
        "South America": "NA",
        "Africa": "EU",
        "Asia": "EU",
        "Oceania": "EU",
    }

    available_rooms = ROOMS[:]
    for mogi in mogi_manager.read_registry().values():
        if mogi.room and mogi.room.name in [room.name for room in available_rooms]:
            available_rooms = [
                room for room in available_rooms if room.name != mogi.room.name
            ]

    room_candidates = [
        room for room in available_rooms if region_to_server[best_region] in room.name
    ]

    return (
        room_candidates[0]
        if room_candidates
        else available_rooms[0] if available_rooms else None
    )
