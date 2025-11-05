from enum import Enum


class archive_type(Enum):
    NO = {"inactive": {"$ne": True}}
    INCLUDE = {}
    ONLY = {"inactive": True}


class sort_type(Enum):
    MMR = "MMR"
    WINS = "Wins"
    LOSSES = "Losses"
    WINRATE = "Winrate %"
