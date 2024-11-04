import requests
from enum import Enum

from models.RoomModel import Room
from config import YUZU_API_URL, YUZU_SERVER_IP, SERVER_MAIN_PORT, SERVER_LOUNGE_PORT


class ServerType(Enum):
    MAIN = "main"
    LOUNGE = "lounge"


def get_room_info(server: ServerType) -> Room:

    try:
        data: dict = (requests.get(f"http://{YUZU_API_URL}/lobby")).json()
        servers: list[dict] = data.get("rooms", [])

        return Room(
            **[
                room
                for room in servers
                if room["address"] == YUZU_SERVER_IP
                and (
                    room["port"] == SERVER_MAIN_PORT
                    if server == ServerType.MAIN
                    else room["port"] == SERVER_LOUNGE_PORT
                )
            ][0]
        )

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []
