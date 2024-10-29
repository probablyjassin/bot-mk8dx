from dataclasses import dataclass
from utils.data.database import db_players

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

    _disconnects: int | None = None
    _inactive: bool | None = None
    _suspended: bool | None = None

    def __init__(
        self,
        _id: ObjectId,
        name: str,
        discord_id: Int64,
        mmr: int,
        history: list[int],
        joined: int | None = None,
        disconnects: int | None = None,
        inactive: bool | None = None,
        suspended: bool | None = None,
    ):
        self._id = _id
        self.name = name
        self.discord_id = discord_id
        self.mmr = mmr
        self.history = history
        self.joined = joined
        self._disconnects = disconnects
        self._inactive = inactive
        self._suspended = suspended

    def __repr__(self):
        return (
            f"PlayerProfile(name={self.name!r}, discord_id={self.discord_id!r}, "
            f"mmr={self.mmr!r}, history=[ {len(self.history)} entries ], joined={self.joined!r}, "
            f"disconnects={self._disconnects!r}, inactive={self._inactive!r}, suspended={self._suspended!r})"
        )

    # Disconnects
    @property
    def disconnects(self) -> int | None:
        return self._disconnects

    @disconnects.getter
    def disconnects(self) -> int | None:
        return self._disconnects

    @disconnects.setter
    def disconnects(self, value: int | None):
        self._disconnects = value
        db_players.update_one(
            {"_id": self._id},
            ({"$set": {"disconnects": value}}),
        )

    # Inactive
    @property
    def inactive(self) -> bool | None:
        return self._inactive

    @inactive.getter
    def inactive(self) -> bool | None:
        return self._inactive

    @inactive.setter
    def inactive(self, value: bool | None):
        self._inactive = value
        db_players.update_one(
            {"_id": self._id},
            ({"$set": {"suspended": value}}),
        )

    @inactive.deleter
    def inactive(self):
        self._inactive = None
        db_players.update_one(
            {"_id": self._id},
            {"$unset": {"inactive": ""}},
        )

    # Suspended
    @property
    def suspended(self) -> bool | None:
        return self._suspended

    @suspended.getter
    def suspended(self) -> bool | None:
        return self._suspended

    @suspended.setter
    def suspended(self, value: bool | None):
        self._suspended = value
        db_players.update_one(
            {"_id": self._id},
            (
                {"$set": {"suspended": value}}
                if value
                else {"$unset": {"suspended": ""}}
            ),
        )

    def to_dict(self) -> dict:
        return {
            "_id": str(self._id),
            "name": self.name,
            "discord_id": self.discord_id,
            "mmr": self.mmr,
            "history": self.history,
            "joined": self.joined,
            "disconnects": self._disconnects,
            "inactive": self._inactive,
            "suspended": self._suspended,
        }

    @classmethod
    def from_dict(cls, data: dict):
        instance = cls(
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
        instance.disconnects = data.get("disconnects")
        instance.inactive = data.get("inactive")
        instance.suspended = data.get("suspended")
        return instance
