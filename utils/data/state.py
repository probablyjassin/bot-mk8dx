import os
import json
from logger import setup_logger
from dataclasses import dataclass

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


state_filename = "state.json"


@dataclass
class BotState:
    def __init__(self):
        os.makedirs("state", exist_ok=True)

    def save_state(self):
        mogi_registry = mogi_manager.read_registry()
        with open(f"state/{state_filename}", "w") as state:
            json.dump(
                {id: mogi_registry[id].to_json() for id in mogi_registry.keys()},
                state,
                indent=4,
            )
        with open("state/state2.json", "w") as state:
            json.dump(
                pretty_format_mogi_dicts(
                    {id: mogi_registry[id].to_json() for id in mogi_registry.keys()}
                ),
                state,
            )

    def manual_save_state(self):
        with open("state/saved.json", "w") as saved:
            mogis = mogi_manager.read_registry()
            json.dump(
                {id: mogis[id].to_json() for id in mogis.keys()},
                saved,
                indent=4,
            )

    def load_saved(self):
        logger.info("Loading state backup...")
        if not os.path.exists(f"state/{state_filename}"):
            logger.info(msg=f"{state_filename} not found - skipping load backup")
            return
        try:
            with open(f"state/{state_filename}", "r") as state:
                data: dict = json.load(state)
                if data:
                    mogi_manager.write_registry(
                        {int(id): Mogi.from_json(data[id]) for id in data.keys()}
                    )
                    logger.info(msg=f"Existing state loaded from {state_filename}")
                else:
                    logger.info(msg=f"No state in {state_filename} - content: <{data}>")
        except json.JSONDecodeError as e:
            error_logger.error(
                f"JSON parsing error in {state_filename}: {e.msg} at line {e.lineno}, column {e.colno}"
            )
            error_logger.error(f"Error position: {e.pos}")
            # Read the file content to show context around the error
            try:
                with open(f"state/{state_filename}", "r") as f:
                    content = f.read()
                    lines = content.split("\n")
                    start_line = max(0, e.lineno - 3)
                    end_line = min(len(lines), e.lineno + 2)
                    error_logger.error("Context around error:")
                    for i in range(start_line, end_line):
                        marker = " --> " if i == e.lineno - 1 else "     "
                        error_logger.error(f"{marker}{i+1}: {lines[i]}")
            except Exception as context_error:
                error_logger.error(f"Could not read file context: {context_error}")
        except Exception as e:
            import traceback

            error_logger.error(
                f"Error loading saved state: {e}\n{traceback.format_exc()}"
            )

    def load_manual_saved(self):
        if not os.path.exists("state/saved.json"):
            return
        with open("state/saved.json", "r") as saved:
            data: dict = json.load(saved)
            if data:
                mogi_manager.write_registry(
                    {int(id): Mogi.from_json(data[id]) for id in data.keys()}
                )


state_manager = BotState()
