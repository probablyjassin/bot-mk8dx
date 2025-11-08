from dataclasses import dataclass, field
from bson.objectid import ObjectId
from bson.int64 import Int64
from utils.data import data_manager


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
        formats (dict{int, int}): A dict of the formats the player played and their amount.
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
    _formats: dict[str, int] = field(
        default_factory=lambda: {str(i): 0 for i in range(7)}
    )
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
        formats,
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
        self._formats = (
            formats if formats is not None else {str(i): 0 for i in range(7)}
        )
        self._joined = joined
        self._disconnects = disconnects
        self._inactive = inactive
        self._suspended = suspended

    # Methods
    async def refresh(self):
        data = await data_manager.Players.find(self._id)
        if data:
            self.__dict__.update(data.__dict__)

    # Properties

    # ID (read-only)
    @property
    def id(self):
        return self._id

    # Name
    @property
    def name(self):
        return self._name

    async def set_name(self, value: str):
        await data_manager.Players.set_attribute(self, "name", value)

    # Discord ID (read-only)
    @property
    def discord_id(self):
        return self._discord_id

    # MMR
    @property
    def mmr(self):
        return self._mmr

    async def set_mmr(self, value):
        await data_manager.Players.set_attribute(self, "mmr", value)

    # History (has different setter)
    @property
    def history(self):
        return self._history

    async def append_history(self, value: int):
        await data_manager.Players.append_history(self, value)

    # Formats
    @property
    def formats(self):
        return self._formats

    async def count_format_played(self, value):
        await data_manager.Players.count_format_played(self, value)

    # Joined (read-only)
    @property
    def joined(self):
        return self._joined

    # Disconnects
    @property
    def disconnects(self):
        return self._disconnects

    async def set_disconnects(self, value):
        await data_manager.Players.set_attribute(self, "disconnects", value)

    async def add_disconnect(self):
        await data_manager.Players.set_attribute(
            self, "disconnects", self._disconnects + 1 if self._disconnects else 1
        )

    # Inactive
    @property
    def inactive(self):
        return self._inactive

    async def set_inactive(self, value):
        await data_manager.Players.set_attribute(self, "inactive", value)

    # Suspended
    @property
    def suspended(self):
        return self._suspended

    async def set_suspended(self, value):
        await data_manager.Players.set_attribute(self, "suspended", value)

    # Dict methods
    def to_json(self) -> dict:
        return {
            "_id": str(self._id),
            "name": self._name,
            "discord_id": self._discord_id,
            "mmr": self._mmr,
            "history": self._history,
            "formats": self._formats,
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
            formats=data["formats"],
            joined=data.get("joined"),
            disconnects=data.get("disconnects"),
            inactive=data.get("inactive"),
            suspended=data.get("suspended"),
        )
        return instance
