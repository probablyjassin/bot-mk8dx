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

    __disconnects__: int | None = None
    __inactive__: bool | None = None
    __suspended__: bool | None = None

    def __repr__(self):
        return (
            f"PlayerProfile(name={self.name!r}, discord_id={self.discord_id!r}, "
            f"mmr={self.mmr!r}, history=[ {len(self.history)} entries ], joined={self.joined!r}, "
            f"disconnects={self.disconnects!r}, inactive={self.inactive!r}, suspended={self.suspended!r})"
        )

    # Disconnects
    @property
    def disconnects(self) -> int | None:
        return self.__disconnects__

    @disconnects.getter
    def disconnects(self) -> int | None:
        return self.__disconnects__

    @disconnects.setter
    def disconnects(self, value: int | None):
        self.__disconnects__ = value
        db_players.update_one(
            {"_id": self._id},
            ({"$set": {"disconnects": value}}),
        )

    # Inactive
    @property
    def inactive(self) -> bool | None:
        return self.__inactive__

    @inactive.getter
    def inactive(self) -> bool | None:
        return self.__inactive__

    @inactive.setter
    def inactive(self, value: bool | None):
        self.__inactive__ = value
        db_players.update_one(
            {"_id": self._id},
            ({"$set": {"suspended": value}}),
        )

    @inactive.deleter
    def inactive(self):
        self.__inactive__ = None
        db_players.update_one(
            {"_id": self._id},
            {"$unset": {"inactive": ""}},
        )

    # Suspended
    @property
    def suspended(self) -> bool | None:
        return self.__suspended__

    @suspended.getter
    def suspended(self) -> bool | None:
        return self.__suspended__

    @suspended.setter
    def suspended(self, value: bool | None):
        self.__suspended__ = value
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
