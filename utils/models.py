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
    status: bool
    player_cap: int
    voting: bool
    running: bool
    password: str | None
    locked: bool
    players: list[MogiPlayer]
    subs: list[MogiPlayer]
    teams: list[list[MogiPlayer]]
    team_tags: list[str]
    calc: list[str]
    points_user: str
    points: list[int]
    input_points: list[int]
    point_count: int
    format: str
    results: list[str]
    placements: list[str]
    voters: list[int]
    votes: dict[str, int]