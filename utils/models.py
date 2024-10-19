from dataclasses import dataclass
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

@dataclass
class Mogi:
    isOpen: bool
    isVoting: bool
    isPlaying: bool
    isFinished: bool

    player_cap: int

    votes: dict[str, int]
    voters: list[int]

    players: list[MogiPlayer]
    subs: list[MogiPlayer]
    teams: list[list[MogiPlayer]]
    team_tags: list[str]

    format: str

    collected_points: list[int]
    calced_results: list[str]
    players_ordered_placements: list[str]