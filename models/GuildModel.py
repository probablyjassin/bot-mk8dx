from dataclasses import dataclass, field
from bson.objectid import ObjectId
from bson.int64 import Int64
from utils.data._database import db_players


@dataclass
class Guild:
    """
    ### Represents a guild's profile. Is obtained and modeled from the database.
    #### Attributes:
        _id (str): The _id assigned by MongoDB.
        name (str): The guild's full official name.
        player_ids (list[Int64]): The Discord IDs of all members. Note: MongoDB converts this to Int64.
        mmr (int): The matchmaking rating of the guild.
        history (list[int]): A list of historical MMR deltas.
        formats (dict{int, int}): A dict of the formats the guild played and their amount.
        joined (int | None): The timestamp when the player joined, or None.
    """

    _id: ObjectId
    _name: str
    _player_ids: list[Int64]
    _mmr: int
    _history: list[int]
    _formats: dict[str, int] = field(
        default_factory=lambda: {str(i): 0 for i in range(7)}
    )
    _joined: int | None = None

    def __init__(
        self,
        _id,
        name,
        player_ids,
        mmr,
        history,
        formats,
        joined=None,
    ):
        self._id = _id
        self._name = name
        self._player_ids = player_ids
        self._mmr = mmr
        self._history = history
        self._formats = (
            formats if formats is not None else {str(i): 0 for i in range(7)}
        )
        self._joined = joined

    # Methods

    """ def update_attribute(self, attr_name: str, value):
        setattr(self, f"_{attr_name}", value)
        db_guilds.update_one(
            {"_id": self._id},
            {"$set": {attr_name: value}},
        ) """

    """ def refresh(self):
        data = db_guilds.find_one({"_id": self._id})
        self.__dict__.update(Guild.from_json(data).__dict__) """

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

    # Discord ID
    @property
    def player_ids(self):
        return self._player_ids

    """ player_ids.setter
    def ... """

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

    # Formats
    @property
    def formats(self):
        return self._formats

    def count_format_played(self, value):
        self._formats[value] += 1
        db_players.update_one(
            {"_id": self._id},
            {"$inc": {f"formats.{value}": 1}},
        )

    # Joined (read-only)
    @property
    def joined(self):
        return self._joined

    # Dict methods
    def to_json(self) -> dict:
        return {
            "_id": str(self._id),
            "name": self._name,
            "player_ids": self._player_ids,
            "mmr": self._mmr,
            "history": self._history,
            "formats": self._formats,
            "joined": self._joined,
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
            player_ids=data["player_ids"],
            mmr=data["mmr"],
            history=data["history"],
            formats=data["formats"],
            joined=data.get("joined"),
        )
        return instance
