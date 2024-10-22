import math
from utils.models.mogi import Rank

ranks = [
    Rank("Wood", (-math.inf, 1)),
    Rank("Bronze", (2, 1499)),
    Rank("Silver", (1400, 2999)),
    Rank("Gold", (3000, 5099)),
    Rank("Platinum", (5100, 6999)),
    Rank("Diamond", (7000, 9499)),
    Rank("Master", (9500, math.inf)),
]

def getRankByMMR(mmr: int) -> Rank:
    for rank in ranks:
        start, end = rank.range[0], rank.range[1]
        if start <= mmr <= end:
            return rank
    return "---"
