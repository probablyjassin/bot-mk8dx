from dataclasses import dataclass


@dataclass
class Rank:
    """
    ### A class to represent a rank a player has depending on their MMR.
    #### Attributes:
        name (str): The name of the rank. Must be one of "Wood", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master".
        range (tuple): A tuple representing the range of values for the rank.
    """

    name: str
    range: tuple[int | float, int | float]

    def __post_init__(self):
        valid_names = {
            "Wood",
            "Bronze",
            "Silver",
            "Gold",
            "Platinum",
            "Diamond",
            "Master",
        }
        if self.name not in valid_names:
            raise ValueError(
                f"Invalid rank name: {self.name}. Must be one of {valid_names}."
            )
