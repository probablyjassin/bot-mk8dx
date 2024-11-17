import math
from dataclasses import dataclass
from enum import Enum
from typing import Union, Tuple


@dataclass
class Rank(Enum):
    """
    ### A class to represent a rank a player has depending on their MMR.
    #### Attributes:
        name (str): The name of the rank. Must be one of "Wood", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master".
        range (tuple): A tuple representing the range of values for the rank.
    """

    WOOD = ("Wood", (-math.inf, 1))
    BRONZE = ("Bronze", (2, 1499))
    SILVER = ("Silver", (1500, 2999))
    GOLD = ("Gold", (3000, 5099))
    PLATINUM = ("Platinum", (5100, 6999))
    DIAMOND = ("Diamond", (7000, 9499))
    MASTER = ("Master", (9500, math.inf))

    def __init__(
        self, rankname: str, mmrrange: Tuple[Union[int, float], Union[int, float]]
    ):
        self.rankname = rankname
        self.mmrrange = mmrrange

    def __str__(self):
        return self.rankname

    @classmethod
    def getRankByMMR(cls, mmr: int) -> "Rank":
        for rank in cls.__members__.values():
            start, end = rank.mmrrange
            if start <= mmr <= end:
                return rank
        return None
