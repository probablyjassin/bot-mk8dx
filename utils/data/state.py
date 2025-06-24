import os
import json
from logger import setup_logger
from dataclasses import dataclass
from collections import OrderedDict

from models.MogiModel import Mogi
from utils.data.mogi_manager import mogi_manager

logger = setup_logger(__name__)
error_logger = setup_logger(__name__, "error.log", console=False)


def pretty_format_mogi_dicts(data: dict[int, dict]) -> str:
    """
    Format mogi data dictionaries with special handling for the players array.
    Each player object in the players array will be on a single line.

    Args:
        data: Dictionary with mogi IDs as keys and mogi JSON data as values

    Returns:
        String containing formatted JSON with indent=4 and special player array formatting
    """
    # Convert to a formatted JSON string
    result = "{\n"

    # Process each mogi
    mogi_ids = sorted(data.keys())
    for i, mogi_id in enumerate(mogi_ids):
        mogi_data = data[mogi_id]

        # Add mogi ID and opening brace
        result += f'    "{mogi_id}": {{\n'

        # Process each key in the mogi
        keys = list(mogi_data.keys())
        for j, key in enumerate(keys):
            value = mogi_data[key]

            # Special handling for players array
            if key == "players" and isinstance(value, list):
                result += '        "players": [\n'

                # Add each player on a single line
                for k, player in enumerate(value):
                    player_json = json.dumps(player)
                    if k < len(value) - 1:
                        result += f"            {player_json},\n"
                    else:
                        result += f"            {player_json}\n"

                result += "        ]"
            else:
                # Normal formatting for other keys
                value_json = json.dumps(value)
                result += f'        "{key}": {value_json}'

            # Add comma if not the last key
            if j < len(keys) - 1:
                result += ",\n"
            else:
                result += "\n"

        # Close mogi object
        if i < len(mogi_ids) - 1:
            result += "    },\n"
        else:
            result += "    }\n"

    # Close the entire JSON object
    result += "}"

    return result


@dataclass
class BotState:
    def __init__(self):
        os.makedirs("state", exist_ok=True)

    def backup(self):
        mogi_registry = mogi_manager.read_registry()
        with open("state/backup.json", "w") as backup:
            json.dump(
                {id: mogi_registry[id].to_json() for id in mogi_registry.keys()},
                backup,
                indent=4,
            )
        with open("state/backup2.json", "w") as backup:
            json.dump(
                pretty_format_mogi_dicts(
                    {id: mogi_registry[id].to_json() for id in mogi_registry.keys()}
                ),
                backup,
            )

    def save(self):
        with open("state/saved.json", "w") as saved:
            mogis = mogi_manager.read_registry()
            json.dump(
                {id: mogis[id].to_json() for id in mogis.keys()},
                saved,
                indent=4,
            )

    def load_backup(self):
        logger.info("Loading state backup...")
        if not os.path.exists("state/backup.json"):
            logger.info(msg="backup.json not found - skipping load backup")
            return
        try:
            with open("state/backup.json", "r") as backup:
                data: dict = json.load(backup)
                if data:
                    mogi_manager.write_registry(
                        {int(id): Mogi.from_json(data[id]) for id in data.keys()}
                    )
                    logger.info(msg="Existing state loaded from backup.json")
                else:
                    logger.info(msg=f"No state in backup.json - content: <{data}>")
        except Exception as e:
            error_logger.error(f"Error loading saved state: {e}")

    def load_saved(self):
        if not os.path.exists("state/saved.json"):
            return
        with open("state/saved.json", "r") as saved:
            data: dict = json.load(saved)
            if data:
                mogi_manager.write_registry(
                    {int(id): Mogi.from_json(data[id]) for id in data.keys()}
                )


state_manager = BotState()
