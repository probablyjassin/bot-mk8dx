from dataclasses import dataclass
from bson.int64 import Int64

@dataclass
class PlayerProfile:
    _id: str
    name: str
    discord_id: Int64
    mmr: int
    history: list[int]
    joined: int | None = None
    disconnects: int | None = None
    inactive: bool | None = None
    suspended: bool | None = None

    def __repr__(self):
        return (f"PlayerProfile(name={self.name!r}, discord_id={self.discord_id!r}, "
                f"mmr={self.mmr!r}, history=[ {len(self.history)} entries ], joined={self.joined!r}, "
                f"disconnects={self.disconnects!r}, inactive={self.inactive!r}, suspended={self.suspended!r})")
