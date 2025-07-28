from dataclasses import dataclass
from models.MogiModel import Mogi


@dataclass
class MogiManager:
    def __init__(self, data: dict[int, Mogi]):
        self._mogi_registry = data

    _mogi_registry: dict[int, Mogi]

    def create_mogi(self, channel_id: int) -> None:
        if channel_id in self._mogi_registry:
            raise ValueError("Mogi with this ID already exists.")
        self._mogi_registry[channel_id] = Mogi(channel_id=channel_id)

    def get_mogi(self, channel_id: int) -> Mogi | None:
        return self._mogi_registry.get(channel_id, None)

    def destroy_mogi(self, channel_id: int) -> None:
        if channel_id not in self._mogi_registry:
            raise ValueError("Mogi with this ID does not exist.")
        del self._mogi_registry[channel_id]

    def write_registry(self, data: dict[int, Mogi]) -> None:
        self._mogi_registry = data

    def read_registry(self) -> dict[int, Mogi]:
        return self._mogi_registry


mogi_manager = MogiManager({})
