import asyncio
import io
import time
from typing import Optional, Tuple, Dict, Any

import aiohttp


class SelectedImageStore:
    """In-memory per-(guild_id, user_id) store with optional image bytes in RAM.

    - Keeps metadata (image_url, source, ts)
    - Optionally stores the actual image bytes, filename, content_type, and size
    - Thread-safe via a single asyncio.Lock (sufficient for this usage)
    - TTL-based expiration on access

    Backward compatible: `get()` still returns a dict, now with extra optional keys:
      bytes (bytes|None), filename (str|None), content_type (str|None), size (int|None)
    """

    def __init__(self, ttl_seconds: Optional[int] = 3600):
        self._data: Dict[Tuple[Optional[int], int], Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._ttl = ttl_seconds

    async def set(
        self,
        guild_id: Optional[int],
        user_id: int,
        image_url: str,
        source_message_url: str,
        *,
        fetch_bytes: bool = False,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
        session: Optional[aiohttp.ClientSession] = None,
        max_bytes: int = 8 * 1024 * 1024,
    ):
        """Save selection. If fetch_bytes=True, also download and keep the image in RAM.

        Args:
            guild_id: Guild identifier (None for DM)
            user_id: User identifier
            image_url: Direct image URL (attachment or embed)
            source_message_url: Message jump URL for reference
            fetch_bytes: When True, downloads the image and stores it in memory
            filename: Optional filename override
            content_type: Optional content-type override
            session: Optional aiohttp session to reuse
            max_bytes: Safety cap for download size
        """
        payload: Dict[str, Any] = {
            "image_url": image_url,
            "source": source_message_url,
            "ts": time.time(),
            # bytes-related (optional)
            "bytes": None,
            "filename": filename,
            "content_type": content_type,
            "size": None,
        }

        if fetch_bytes:
            fetched = await self._fetch_image(
                image_url, session=session, max_bytes=max_bytes
            )
            if fetched is not None:
                b, ct, fn = fetched
                payload["bytes"] = b
                payload["size"] = len(b)
                # Only set if not overridden
                payload["content_type"] = content_type or ct
                payload["filename"] = filename or fn

        async with self._lock:
            self._data[(guild_id, user_id)] = payload

    async def set_bytes(
        self,
        guild_id: Optional[int],
        user_id: int,
        image_bytes: bytes,
        *,
        filename: str = "image",
        content_type: Optional[str] = None,
        source_message_url: str,
        image_url: Optional[str] = None,
    ):
        """Save pre-fetched image bytes directly."""
        async with self._lock:
            self._data[(guild_id, user_id)] = {
                "image_url": image_url,
                "source": source_message_url,
                "ts": time.time(),
                "bytes": image_bytes,
                "filename": filename,
                "content_type": content_type,
                "size": len(image_bytes) if image_bytes is not None else None,
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

    async def get_bytes(self, guild_id: Optional[int], user_id: int) -> Optional[bytes]:
        """Convenience to get raw bytes if stored (None when not fetched or expired)."""
        record = await self.get(guild_id, user_id)
        if record is None:
            return None
        return record.get("bytes")

    async def to_discord_file(
        self,
        guild_id: Optional[int],
        user_id: int,
        *,
        default_filename: str = "image.png",
    ):
        """Return a discord.File if bytes are present, else None.

        Import is local to avoid hard dependency at module import time.
        """
        record = await self.get(guild_id, user_id)
        if not record or not record.get("bytes"):
            return None
        try:
            # Local import to avoid circulars/optional dependency issues
            import discord  # type: ignore
        except Exception:
            return None

        file_name = record.get("filename") or default_filename
        b = record["bytes"]
        return discord.File(fp=io.BytesIO(b), filename=file_name)

    async def clear(self, guild_id: Optional[int], user_id: int):
        async with self._lock:
            self._data.pop((guild_id, user_id), None)

    async def _fetch_image(
        self,
        url: str,
        *,
        session: Optional[aiohttp.ClientSession] = None,
        max_bytes: int = 8 * 1024 * 1024,
    ) -> Optional[Tuple[bytes, Optional[str], Optional[str]]]:
        """Download image bytes with a size cap.

        Returns: (bytes, content_type, filename) or None on failure.
        """
        owns_session = False
        sess = session
        if sess is None:
            sess = aiohttp.ClientSession()
            owns_session = True
        try:
            async with sess.get(url) as resp:
                if resp.status != 200:
                    return None
                content_type = resp.headers.get("Content-Type")
                # Derive filename from Content-Disposition or URL path
                filename = None
                cd = resp.headers.get("Content-Disposition")
                if cd and "filename=" in cd:
                    filename = cd.split("filename=")[-1].strip('"')
                if not filename:
                    try:
                        from urllib.parse import urlparse

                        path = urlparse(url).path
                        if path:
                            filename = path.rsplit("/", 1)[-1] or None
                    except Exception:
                        filename = None

                # Read with cap
                buf = bytearray()
                async for chunk in resp.content.iter_chunked(64 * 1024):
                    buf.extend(chunk)
                    if len(buf) > max_bytes:
                        return None
                return bytes(buf), content_type, filename
        except Exception:
            return None
        finally:
            if owns_session:
                await sess.close()


store = SelectedImageStore(ttl_seconds=5 * 60)  # keep for 5 minutes
