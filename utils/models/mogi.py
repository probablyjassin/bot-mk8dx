from dataclasses import dataclass, field
from bson.int64 import Int64
from utils.maths.teams import distribute_players_to_teams

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

def e():
    return []

def default_votes():
    return { "ffa": 0, "2v2": 0, "3v3": 0, "4v4": 0, "5v5": 0, "6v6": 0 }

def default_team_tags():
    return ["Team 1", "Team 2", "Team 3", "Team 4", "Team 5", "Team 6"]

@dataclass
class Mogi:
    channel_id: int

    isVoting: bool = False
    isPlaying: bool = False
    isFinished: bool = False
    format: int | None = None

    player_cap: int = 12

    votes: dict[str, int] = field(default_factory=default_votes)
    voters: list[int] = field(default_factory=e)

    players: list[PlayerProfile] = field(default_factory=e)
    subs: list[PlayerProfile] = field(default_factory=e)
    teams: list[list[PlayerProfile]] = field(default_factory=e)
    team_tags: list[str] = field(default_factory=default_team_tags)

    collected_points: list[int] = field(default_factory=e)
    calced_results: list[str] = field(default_factory=e)
    players_ordered_placements: list[str] = field(default_factory=e)

    def play(self, format_int: int) -> None:
        self.format = format_int

        if format_int == 1:
            for player in self.players:
                self.teams.append([player])

        else:
            self.teams = distribute_players_to_teams(self.players, format_int)
        
        self.isVoting = False
        self.isPlaying = True

        self.voters = []
        self.votes = {key: 0 for key in self.votes}

@dataclass
class Rank:
    name: str
    range: tuple[int | float, int | float]

    def __post_init__(self):
        valid_names = {"Wood", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master"}
        if self.name not in valid_names:
            raise ValueError(f"Invalid rank name: {self.name}. Must be one of {valid_names}.")
