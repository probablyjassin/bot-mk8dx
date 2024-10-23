from dataclasses import dataclass

@dataclass
class Rank:
    name: str
    range: tuple[int | float, int | float]

    def __post_init__(self):
        valid_names = {"Wood", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master"}
        if self.name not in valid_names:
            raise ValueError(f"Invalid rank name: {self.name}. Must be one of {valid_names}.")
