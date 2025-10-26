import asyncio
import time
from typing import Optional, Tuple


class SelectedImageStore:
    """In-memory per-(guild_id, user_id) store with a tiny lock."""

    def __init__(self, ttl_seconds: Optional[int] = 3600):
        self._data: dict[Tuple[Optional[int], int], dict] = {}
        self._lock = asyncio.Lock()
        self._ttl = ttl_seconds

    async def set(
        self,
        guild_id: Optional[int],
        user_id: int,
        image_url: str,
        source_message_url: str,
    ):
        async with self._lock:
            self._data[(guild_id, user_id)] = {
                "image_url": image_url,
                "source": source_message_url,
                "ts": time.time(),
            }

    async def get(self, guild_id: Optional[int], user_id: int) -> Optional[dict]:
        async with self._lock:
            record = self._data.get((guild_id, user_id))
            if not record:
                return None
            if self._ttl and (time.time() - record["ts"]) > self._ttl:
                # Expire
                del self._data[(guild_id, user_id)]
                return None
            return record

    async def clear(self, guild_id: Optional[int], user_id: int):
        async with self._lock:
            self._data.pop((guild_id, user_id), None)


store = SelectedImageStore(ttl_seconds=5 * 60)  # keep for 5 minutes
