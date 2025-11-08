from dataclasses import dataclass
from bson.objectid import ObjectId
from bson.int64 import Int64
from models.PlayerModel import PlayerProfile
from utils.data.data_manager import data_manager


@dataclass
class Guild:
    """
    ### Represents a guild's profile. Is obtained and modeled from the database.
    #### Attributes:
        _id (str): The _id assigned by MongoDB.
        name (str): The guild's full official name.
        icon (str): Static URL to the Guild Icon image.
        player_ids (list[Int64]): The Discord IDs of all members. Note: MongoDB converts this to Int64.
        mmr (int): The matchmaking rating of the guild.
        history (list[int]): A list of historical MMR deltas.
        creation_date (int | None): The timestamp when the player joined, or None.
    """

    _id: ObjectId
    _name: str
    _icon: str
    _player_ids: list[Int64]
    _mmr: int
    _history: list[int]
    _creation_date: int | None = None

    def __init__(self, _id, name, icon, player_ids, mmr, history, creation_date):
        self._id = _id
        self._name = name
        self._icon = icon
        self._player_ids = player_ids
        self._mmr = mmr
        self._history = history
        self._creation_date = creation_date

    # Getters and Setters

    # name
    @property
    def name(self) -> str:
        return self._name

    async def set_name(self, value: str):
        await data_manager.Guilds.set_attribute(self, "name", value)

    # icon
    @property
    def icon(self) -> str:
        return self._icon

    @icon.setter
    def icon(self, value: str):
        self._icon = value

    # mmr
    @property
    def mmr(self) -> str:
        return self._mmr

    @mmr.setter
    def mmr(self, value: str):
        self._mmr = value

    # creation_date
    @property
    def creation_date(self) -> int | None:
        return self._creation_date

    # player_ids
    @property
    def player_ids(self) -> list[Int64]:
        return self._player_ids

    def append_player_id(self, player_id: Int64):
        self._player_ids.append(player_id)

    def remove_player_id(self, player_id: Int64):
        if player_id in self._player_ids:
            self._player_ids.remove(player_id)

    # history
    @property
    def history(self) -> list[int]:
        return self._history

    def append_history(self, value: int):
        self._history.append(value)

    async def fetch_player_profiles(self) -> list[PlayerProfile]:
        return await data_manager.Players.find_list(self.player_ids)

    # Properties

    # Dict methods
    def to_json(self) -> dict:
        return {
            "_id": str(self._id),
            "name": self._name,
            "player_ids": self._player_ids,
            "mmr": self._mmr,
            "history": self._history,
            "joined": self._creation_date,
        }

    def to_mongo(self) -> dict:
        self_json = self.to_json()
        self_json["_id"] = self._id
        self_json["_player_ids"] = [Int64(pid) for pid in self._player_ids]
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
