from dataclasses import dataclass
from bson.int64 import Int64
from bson import ObjectId


@dataclass
class PlayerProfile:
    """
    ### Represents a player's profile. Is obtained and modeled from the database.
    #### Attributes:
        _id (str): The _id assigned by MongoDB.
        name (str): The username of the player.
        discord_id (Int64): The Discord ID of the player. Note: MongoDB converts this to Int64.
        mmr (int): The matchmaking rating of the player.
        history (list[int]): A list of historical MMR deltas.
        joined (int | None): The timestamp when the player joined, or None.
        disconnects (int | None): The number of times the player has disconnected, or None.
        inactive (bool | None): Indicates player inactivity, usually None.
        suspended (bool | None): Indicates player suspension, usually None.
    """

    _id: ObjectId
    name: str
    discord_id: Int64
    mmr: int
    history: list[int]
    joined: int | None = None
    disconnects: int | None = None
    inactive: bool | None = None
    suspended: bool | None = None

    def __repr__(self):
        return (
            f"PlayerProfile(name={self.name!r}, discord_id={self.discord_id!r}, "
            f"mmr={self.mmr!r}, history=[ {len(self.history)} entries ], joined={self.joined!r}, "
            f"disconnects={self.disconnects!r}, inactive={self.inactive!r}, suspended={self.suspended!r})"
        )

    def to_dict(self) -> dict:
        return {
            "_id": str(self._id),
            "name": self.name,
            "discord_id": self.discord_id,
            "mmr": self.mmr,
            "history": self.history,
            "joined": self.joined,
            "disconnects": self.disconnects,
            "inactive": self.inactive,
            "suspended": self.suspended,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            _id=ObjectId(data["_id"]),
            name=data["name"],
            discord_id=Int64(data["discord_id"]),
            mmr=data["mmr"],
            history=data["history"],
            joined=data.get("joined"),
            disconnects=data.get("disconnects"),
            inactive=data.get("inactive"),
            suspended=data.get("suspended"),
        )
