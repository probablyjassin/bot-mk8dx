from dataclasses import dataclass, field
from discord.ext import commands
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

    def __repr__(self):
        return (f"PlayerProfile(name={self.name!r}, discord_id={self.discord_id!r}, "
                f"mmr={self.mmr!r}, history=[ {len(self.history)} entries ], joined={self.joined!r}, "
                f"disconnects={self.disconnects!r}, inactive={self.inactive!r})")

def emtpty_list():
    return []

def default_team_tags():
    return ["Team 1", "Team 2", "Team 3", "Team 4", "Team 5", "Team 6"]

@dataclass
class Mogi:
    channel_id: int

    isVoting: bool = False
    isPlaying: bool = False
    isFinished: bool = False

    player_cap: int = 12

    votes: dict[str, int] = field(default_factory=emtpty_list)
    voters: list[int] = field(default_factory=emtpty_list)

    players: list[PlayerProfile] = field(default_factory=emtpty_list)
    subs: list[PlayerProfile] = field(default_factory=emtpty_list)
    teams: list[list[PlayerProfile]] = field(default_factory=emtpty_list)
    team_tags: list[str] = field(default_factory=default_team_tags)

    format: str = ""

    collected_points: list[int] = field(default_factory=emtpty_list)
    calced_results: list[str] = field(default_factory=emtpty_list)
    players_ordered_placements: list[str] = field(default_factory=emtpty_list)