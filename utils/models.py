from dataclasses import dataclass, field
from utils.database import db

@dataclass
class PlayerProfile:
    name: str
    discord_id: int
    mmr: int
    history: list[int]
    disconnects: int | None
    inactive: bool | None

@dataclass
class MogiPlayer:
    discord_id: int

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

    players: list[MogiPlayer] = field(default_factory=emtpty_list)
    subs: list[MogiPlayer] = field(default_factory=emtpty_list)
    teams: list[list[MogiPlayer]] = field(default_factory=emtpty_list)
    team_tags: list[str] = field(default_factory=default_team_tags)

    format: str = ""

    collected_points: list[int] = field(default_factory=emtpty_list)
    calced_results: list[str] = field(default_factory=emtpty_list)
    players_ordered_placements: list[str] = field(default_factory=emtpty_list)