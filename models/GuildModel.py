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


@dataclass
class PlayingGuild(Guild):
    """
    ### Represents a guild with active player objects (bot-side only, not stored in DB).
    Inherits from Guild but includes actual PlayerProfile objects for members.
    #### Additional Attributes:
        members (list[PlayerProfile]): List of all member PlayerProfile objects.
        playing (list[PlayerProfile]): List of members currently playing.
    """

    def __init__(
        self,
        guild: Guild,
        playing: list[PlayerProfile] = None,
        subs: list[PlayerProfile] = None,
    ):
        super().__init__(
            _id=guild._id,
            name=guild._name,
            icon=guild._icon,
            player_ids=guild._player_ids,
            mmr=guild._mmr,
            history=guild._history,
            creation_date=guild._creation_date,
        )
        self._playing: list[PlayerProfile] = playing or []
        self._subs: list[PlayerProfile] = subs or []

    # playing
    @property
    def playing(self) -> list[PlayerProfile]:
        return self._playing

    def set_playing(self, value: list[PlayerProfile]):
        self._playing = value

    def add_playing(self, player: PlayerProfile):
        if player.discord_id in self.player_ids and player not in self._playing:
            self._playing.append(player)

    def remove_playing(self, player: PlayerProfile):
        if player in self._playing:
            self._playing.remove(player)

    def clear_playing(self):
        self._playing.clear()

    # subs
    @property
    def subs(self) -> list[PlayerProfile]:
        return self._subs

    def set_subs(self, value: list[PlayerProfile]):
        self._subs = value

    def add_sub(self, player: PlayerProfile):
        if (
            player.discord_id in self.player_ids
            and player not in self._playing
            and player not in self._subs
        ):
            self._subs.append(player)

    def remove_sub(self, player: PlayerProfile):
        if player in self._subs:
            self._subs.remove(player)

    def clear_subs(self):
        self._subs.clear()

    # Override to_mongo to ensure DB operations only use base Guild data
    def to_mongo(self) -> dict:
        # Use parent's to_mongo to avoid serializing members/playing
        return super().to_mongo()

    # Override to_json to exclude members/playing from serialization
    def to_json(self) -> dict:
        # Use parent's to_json to avoid serializing members/playing
        return super().to_json()

    @classmethod
    def from_json(cls, data):
        # Create base Guild from data
        base_guild = Guild.from_json(data)

        # Extract playing and subs if present
        playing = []
        if "playing" in data:
            playing = [PlayerProfile.from_json(p) for p in data["playing"]]

        subs = []
        if "subs" in data:
            subs = [PlayerProfile.from_json(s) for s in data["subs"]]

        return cls(base_guild, playing=playing, subs=subs)

    def to_json_full(self) -> dict:
        return {
            "_id": str(self._id),
            "name": self._name,
            "player_ids": self._player_ids,
            "mmr": self._mmr,
            "history": self._history,
            "joined": self._creation_date,
            "playing": [player.to_json() for player in self._playing],
            "subs": [player.to_json() for player in self._subs],
        }
