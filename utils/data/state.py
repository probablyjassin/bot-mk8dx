import os
import json
import redis
from logger import setup_logger
from dataclasses import dataclass

from models.MogiModel import Mogi
from utils.data.mogi_manager import mogi_manager
from utils.data.guild_manager import guild_manager
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD

logger = setup_logger(__name__)
error_logger = setup_logger(__name__, "error.log", console=False)

# Redis keys used for central state
STATE_MOGIS_KEY = "state:mogis"
STATE_GUILD_QUEUE_KEY = "state:guild_queue"
STATE_SAVED_KEY = "state:saved"


@dataclass
class BotState:
    def __init__(self):
        os.makedirs("state", exist_ok=True)
        # initialize redis client
        try:
            self.r = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True,
            )
            # quick ping to detect connection issues early
            try:
                self.r.ping()
            except Exception:
                logger.info(
                    "Redis not available at init; continuing and retrying on operations"
                )
        except Exception as e:
            self.r = None
            error_logger.error(f"Failed to initialize Redis client: {e}")

    def save_state(self):
        mogi_registry = mogi_manager.read_registry()
        guild_queue = guild_manager.read_registry()

        # Save mogi registry to redis
        try:
            if self.r:
                mogis_payload = {
                    id: mogi_registry[id].to_json() for id in mogi_registry.keys()
                }
                self.r.set(STATE_MOGIS_KEY, json.dumps(mogis_payload))
            else:
                raise RuntimeError("Redis client unavailable")
        except Exception as e:
            error_logger.error(f"Error saving mogi registry to redis: {e}")

        # Save guild queue to redis
        try:
            if self.r:
                self.r.set(STATE_GUILD_QUEUE_KEY, json.dumps(guild_queue))
            else:
                raise RuntimeError("Redis client unavailable")
        except Exception as e:
            error_logger.error(f"Error saving guild queue to redis: {e}")

    def manual_save_state(self):
        mogis = mogi_manager.read_registry()
        try:
            if self.r:
                self.r.set(
                    STATE_SAVED_KEY,
                    json.dumps({id: mogis[id].to_json() for id in mogis.keys()}),
                )
            else:
                raise RuntimeError("Redis client unavailable")
        except Exception as e:
            error_logger.error(f"Error saving manual saved state to redis: {e}")

    def load_saved(self):
        logger.info("Loading state backup...")

        # Load mogi registry backup from redis
        try:
            if not self.r:
                raise RuntimeError("Redis client unavailable")

            data_raw = self.r.get(STATE_MOGIS_KEY)
            if not data_raw:
                logger.info(msg=f"{STATE_MOGIS_KEY} not found - skipping load backup")
            else:
                try:
                    data: dict = json.loads(data_raw)
                    if data:
                        mogi_manager.write_registry(
                            {int(id): Mogi.from_json(data[id]) for id in data.keys()}
                        )
                        logger.info(msg=f"Existing state loaded from {STATE_MOGIS_KEY}")
                    else:
                        logger.info(
                            msg=f"No state in {STATE_MOGIS_KEY} - content: <{data}>"
                        )
                except json.JSONDecodeError as e:
                    error_logger.error(
                        f"JSON parsing error in {STATE_MOGIS_KEY}: {e.msg} at line {e.lineno}, column {e.colno}"
                    )
        except Exception as e:
            import traceback

            error_logger.error(
                f"Error loading saved state from redis: {e}\n{traceback.format_exc()}"
            )

        # Load Guild Queue Backup from redis
        logger.info("Loading guild queue backup...")
        try:
            if not self.r:
                raise RuntimeError("Redis client unavailable")

            data_raw = self.r.get(STATE_GUILD_QUEUE_KEY)
            if not data_raw:
                logger.info(
                    msg=f"{STATE_GUILD_QUEUE_KEY} not found - skipping load guild queue"
                )
                return
            try:
                data: dict = json.loads(data_raw)
                if data:
                    guild_manager.write_registry(data=data)
                    logger.info(
                        msg=f"Existing state loaded from {STATE_GUILD_QUEUE_KEY}"
                    )
                else:
                    logger.info(
                        msg=f"No state in {STATE_GUILD_QUEUE_KEY} - content: <{data}>"
                    )
            except json.JSONDecodeError as e:
                error_logger.error(
                    f"JSON parsing error in {STATE_GUILD_QUEUE_KEY}: {e.msg} at line {e.lineno}, column {e.colno}"
                )
        except Exception as e:
            error_logger.error(f"Error loading guild queue from redis: {e}")

    def load_manual_saved(self):
        try:
            if not self.r:
                raise RuntimeError("Redis client unavailable")

            data_raw = self.r.get(STATE_SAVED_KEY)
            if not data_raw:
                return
            data: dict = json.loads(data_raw)
            if data:
                mogi_manager.write_registry(
                    {int(id): Mogi.from_json(data[id]) for id in data.keys()}
                )
        except Exception as e:
            error_logger.error(f"Error loading manual saved state from redis: {e}")


state_manager = BotState()
