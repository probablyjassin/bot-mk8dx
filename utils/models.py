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
    channel_id: int

    isVoting: bool = False
    isPlaying: bool = False
    isFinished: bool = False

    player_cap: int = 12

    votes: dict[str, int] = []
    voters: list[int] = []

    players: list[MogiPlayer] = []
    subs: list[MogiPlayer] = []
    teams: list[list[MogiPlayer]] = []
    team_tags: list[str] = ["Team 1", "Team 2", "Team 3", "Team 4", "Team 5", "Team 6"] 

    format: str = ""

    collected_points: list[int] = []
    calced_results: list[str] = []
    players_ordered_placements: list[str] = []