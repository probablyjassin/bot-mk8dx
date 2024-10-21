from dataclasses import dataclass, field
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

@dataclass
class Rank:
    name: str
    range: tuple[int | float, int | float]

    def __post_init__(self):
        valid_names = {"Wood", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master"}
        if self.name not in valid_names:
            raise ValueError(f"Invalid rank name: {self.name}. Must be one of {valid_names}.")
