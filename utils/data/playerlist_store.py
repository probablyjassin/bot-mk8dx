import asyncio
from typing import Dict, Any, Optional


class player_alias_store:
    def __init__(self):
        self._data: Dict[int, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def set(self, channel_id: int, key: str, value: Any):
        """Set a single key's value for this channel_id."""
        async with self._lock:
            self._data.setdefault(channel_id, {})[key] = value

    async def update(self, channel_id: int, values: Dict[str, Any]):
        """Set multiple keys at once for this channel_id."""
        async with self._lock:
            self._data.setdefault(channel_id, {}).update(values)

    async def get(self, channel_id: int, key: str, default: Any = None) -> Any:
        """Get a single key's value, or `default` if missing."""
        async with self._lock:
            record = self._data.get(channel_id)
            if record is None:
                return default
            return record.get(key, default)

    async def get_all(self, channel_id: int) -> Optional[Dict[str, Any]]:
        """Get the full record dict for this channel_id, or None if missing."""
        async with self._lock:
            return self._data.get(channel_id)

    async def delete_key(self, channel_id: int, key: str):
        """Remove a single key from this channel_id's record, if present."""
        async with self._lock:
            record = self._data.get(channel_id)
            if record is not None:
                record.pop(key, None)

    async def clear(self, channel_id: int):
        """Remove the entire record for this channel_id."""
        async with self._lock:
            self._data.pop(channel_id, None)


store = player_alias_store()