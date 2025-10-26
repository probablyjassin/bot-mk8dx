from utils.data.mogi_manager import mogi_manager
from models.MogiModel import Mogi
from models.RoomModel import Room

from config import ROOMS_CONFIG

ROOMS: list[Room] = [
    Room.from_address(room["address"], room["port"]) for room in ROOMS_CONFIG
]


async def get_available_server(mogi: Mogi) -> Room | None:
    available_rooms = ROOMS[:]
    for mogi in mogi_manager.read_registry().values():
        if mogi.room and mogi.room.name in [room.name for room in available_rooms]:
            available_rooms = [
                room for room in available_rooms if room.name != mogi.room.name
            ]

    return available_rooms[0] if available_rooms else None
