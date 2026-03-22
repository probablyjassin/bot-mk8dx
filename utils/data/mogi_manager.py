from dataclasses import dataclass
from models.MogiModel import Mogi


@dataclass
class MogiManager:
    def __init__(self):
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        db = int(os.getenv("REDIS_DB", 0))
        password = os.getenv("REDIS_PASSWORD", None)

        self.r = redis.Redis(
            host=host, port=port, db=db, password=password, decode_responses=True
        )
        self.prefix = "mogi:"

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


import redis
import json
from models.MogiModel import Mogi
from config import REDIS_HOST, REDIS_DB, REDIS_PORT, REDIS_PASSWORD


class MogiManager:
    def __init__(self):
        self.r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True,
        )
        self.prefix = "mogi:"

    def _get_key(self, channel_id: int) -> str:
        return f"{self.prefix}{channel_id}"

    def create_mogi(self, channel_id: int) -> None:
        key = self._get_key(channel_id)
        if self.r.exists(key):
            raise ValueError("Mogi with this ID already exists.")

        new_mogi = Mogi(channel_id=channel_id)
        # Convert dataclass to dict, then to JSON string
        self.r.set(key, json.dumps(new_mogi.__dict__))

    def get_mogi(self, channel_id: int) -> Mogi | None:
        data = self.r.get(self._get_key(channel_id))
        if not data:
            return None

        # Parse JSON and reconstruct the Mogi object
        mogi_dict = json.loads(data)
        return Mogi(**mogi_dict)  # Or use dacite.from_dict(Mogi, mogi_dict)

    def save_mogi(self, mogi: Mogi) -> None:
        """New helper to update an existing Mogi in Redis"""
        key = self._get_key(mogi.channel_id)
        self.r.set(key, json.dumps(mogi.__dict__))

    def destroy_mogi(self, channel_id: int) -> None:
        if not self.r.delete(self._get_key(channel_id)):
            raise ValueError("Mogi with this ID does not exist.")

    def read_all_mogi_ids(self) -> list[int]:
        """Replacement for reading the whole registry keys"""
        keys = self.r.keys(f"{self.prefix}*")
        return [int(k.split(":")[1]) for k in keys]


# Global instance
mogi_manager = MogiManager()
