from dataclasses import dataclass
from bson.objectid import ObjectId
from bson.int64 import Int64
from utils.data.database import db_players


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
    _name: str
    _discord_id: Int64
    _mmr: int
    _history: list[int]
    _joined: int | None = None

    _disconnects: int | None = None
    _inactive: bool | None = None
    _suspended: bool | None = None

    def __init__(
        self,
        _id,
        name,
        discord_id,
        mmr,
        history,
        joined=None,
        disconnects=None,
        inactive=None,
        suspended=None,
    ):
        self._id = _id
        self._name = name
        self._discord_id = discord_id
        self._mmr = mmr
        self._history = history
        self._joined = joined
        self._disconnects = disconnects
        self._inactive = inactive
        self._suspended = suspended

    # Methods

    def update_attribute(self, attr_name, value):
        setattr(self, f"_{attr_name}", value)
        db_players.update_one(
            {"_id": self._id},
            {"$set": {attr_name: value}},
        )

    def refresh(self):
        data = db_players.find_one({"_id": self._id})
        self.__dict__.update(PlayerProfile.from_json(data).__dict__)

    # Properties

    # ID (read-only)
    @property
    def id(self):
        return self._id

    # Name
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self.update_attribute("name", value)

    # Discord ID (read-only)
    @property
    def discord_id(self):
        return self._discord_id

    # MMR
    @property
    def mmr(self):
        return self._mmr

    @mmr.setter
    def mmr(self, value):
        self.update_attribute("mmr", value)

    # History (has different setter)
    @property
    def history(self):
        return self._history

    def append_history(self, value):
        self._history.append(value)
        db_players.update_one(
            {"_id": self._id},
            {"$push": {"history": value}},
        )

    # Joined (read-only)
    @property
    def joined(self):
        return self._joined

    # Disconnects
    @property
    def disconnects(self):
        return self._disconnects

    @disconnects.setter
    def disconnects(self, value):
        if value == 0:
            del self.disconnects
            return
        self.update_attribute("disconnects", value)

    @disconnects.deleter
    def disconnects(self):
        self._disconnects = None
        db_players.update_one(
            {"_id": self._id},
            {"$unset": {"disconnects": ""}},
        )

    def add_disconnect(self):
        db_players.update_one(
            {"_id": self._id},
            (
                {"$inc": {"disconnects": 1}}
                if self._disconnects
                else {"$set": {"disconnects": 1}}
            ),
        )
        self._disconnects = self._disconnects + 1 if self._disconnects else 1

    # Inactive
    @property
    def inactive(self):
        return self._inactive

    @inactive.setter
    def inactive(self, value):
        self.update_attribute("inactive", value)

    # Custom deleter
    @inactive.deleter
    def inactive(self):
        self._inactive = None
        db_players.update_one(
            {"_id": self._id},
            {"$unset": {"inactive": ""}},
        )

    # Suspended
    @property
    def suspended(self):
        return self._suspended

    @suspended.setter
    def suspended(self, value):
        self.update_attribute("suspended", value)

    # Custom deleter
    @suspended.deleter
    def inactive(self):
        self._suspended = None
        db_players.update_one(
            {"_id": self._id},
            {"$unset": {"suspended": ""}},
        )

    # Dict methods
    def to_json(self) -> dict:
        return {
            "_id": str(self._id),
            "name": self._name,
            "discord_id": self._discord_id,
            "mmr": self._mmr,
            "history": self._history,
            "joined": self._joined,
            "disconnects": self._disconnects,
            "inactive": self._inactive,
            "suspended": self._suspended,
        }

    def to_mongo(self) -> dict:
        self_json = self.to_json()
        self_json["_id"] = self._id
        return self_json

    @classmethod
    def from_json(cls, data: dict):
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
