import requests
from dataclasses import dataclass

from config import YUZU_API_URL


@dataclass
class Room:
    """Represents a yuzu server/room.
    This class handles servers used for mogis, including room properties
    and player information.
    Attributes:
        address (str): The IP address of the room server.
        description (str): A description of the room.
        externalGuid (str): External unique identifier for the room.
        hasPassword (bool): Whether the room is password protected.
        id (str): Unique identifier for the room.
        maxPlayers (int): Maximum number of players allowed in the room.
        name (str): Name of the room.
        netVersion (int): Network protocol version.
        owner (str): Name or identifier of the room owner.
        players (list[dict]): List of players currently in the room.
        port (int): Port number used by the room server.
        preferredGameId (int): ID of the preferred game for this room.
        preferredGameName (str): Name of the preferred game for this room.
    Methods:
        most_popular_game() -> tuple[int, str] | None:
            Returns the count and name of the most played game in the room.
            Returns None if no players are present.
        from_address(address: str, port: int) -> Room | None:
            Creates a Room instance from server address and port.
            Returns None if room is not found or on connection error.
        to_json() -> dict:
            Converts the Room instance to a JSON-compatible dictionary.
        from_json(json_data: dict | None) -> Room | None:
            Creates a Room instance from JSON data.
            Returns None if json_data is None.
    """

    address: str
    description: str
    externalGuid: str
    hasPassword: bool
    id: str
    maxPlayers: int
    name: str
    netVersion: int
    owner: str
    players: list[dict]
    port: int
    preferredGameId: int
    preferredGameName: str

    def most_popular_game(self) -> tuple[int, str] | None:
        game_count = {}
        for player in self.players:
            game_name = player["gameName"]
            if game_name in game_count:
                game_count[game_name] += 1
            else:
                game_count[game_name] = 1
        if game_count == {}:
            return None
        most_popular = max(game_count, key=game_count.get)
        return (game_count[most_popular], most_popular)

    # WIP
    @classmethod
    def from_address(cls, address: str, port: int) -> "Room | None":
        try:
            data: dict = (requests.get(f"http://{YUZU_API_URL}/lobby")).json()
            servers: list[dict] = data.get("rooms", [])

            potential_rooms = [
                room
                for room in servers
                if room["address"] == address and room["port"] == port
            ]

            if potential_rooms:
                return cls(**potential_rooms[0])
            else:
                return None

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def refresh(self) -> None:
        data: dict = (requests.get(f"http://{YUZU_API_URL}/lobby")).json()
        servers: list[dict] = data.get("rooms", [])
        candidates = [
            entry
            for entry in servers
            if entry["address"] == self.address and entry["port"] == self.port
        ]
        server = None
        if candidates:
            server = candidates[0]
        if not server:
            return None
        updated_room = Room.from_json(server)

        # Update this instance's attributes with the new values
        for key, value in updated_room.__dict__.items():
            setattr(self, key, value)
        return self

    def to_json(self) -> dict:
        return {
            "address": self.address,
            "description": self.description,
            "externalGuid": self.externalGuid,
            "hasPassword": self.hasPassword,
            "id": self.id,
            "maxPlayers": self.maxPlayers,
            "name": self.name,
            "netVersion": self.netVersion,
            "owner": self.owner,
            "players": self.players,
            "port": self.port,
            "preferredGameId": self.preferredGameId,
            "preferredGameName": self.preferredGameName,
        }

    @classmethod
    def from_json(cls, json_data: dict | None) -> "Room | None":
        return (
            cls(
                address=json_data["address"],
                description=json_data["description"],
                externalGuid=json_data["externalGuid"],
                hasPassword=json_data["hasPassword"],
                id=json_data["id"],
                maxPlayers=json_data["maxPlayers"],
                name=json_data["name"],
                netVersion=json_data["netVersion"],
                owner=json_data["owner"],
                players=json_data["players"],
                port=json_data["port"],
                preferredGameId=json_data["preferredGameId"],
                preferredGameName=json_data["preferredGameName"],
            )
            if json_data
            else None
        )
