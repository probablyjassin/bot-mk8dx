from dataclasses import dataclass, field
from models.MogiModel import Mogi


@dataclass
class MiniMogi(Mogi):
    """
    ### Represents a Mini Mogi in a discord channel. (Inherits from `Mogi`)
    """

    @classmethod
    def from_mogi(cls, mogi: Mogi) -> "MiniMogi":
        """Convert a Mogi instance to a MiniMogi instance."""
        return cls(**mogi.to_json())
