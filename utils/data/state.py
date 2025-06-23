import os
import json
from logger import setup_logger
from dataclasses import dataclass
from collections import OrderedDict

from models.MogiModel import Mogi
from utils.data.mogi_manager import mogi_manager

logger = setup_logger(__name__)
error_logger = setup_logger(__name__, "error.log", console=False)


def pretty_format_mogi(data: dict) -> str:
    """
    Saves a dictionary to a JSON file with normal indent=4 formatting,
    but with each entry in a specified list (e.g., "players") taking up
    an individual line as a single-line JSON object.

    Args:
        data (dict): The dictionary to save.
    """
    indent_level = 4
    players_key = "players"

    # Create a deep copy to avoid modifying the original dictionary during processing
    data_copy = json.loads(
        json.dumps(data)
    )  # Simple way to deep copy a JSON-serializable dict

    if players_key in data_copy and isinstance(data_copy[players_key], list):
        player_list = data_copy[players_key]
        formatted_players_items = []
        for player_obj in player_list:
            # Dump each player object as a compact, single-line JSON string
            # and add the correct indentation for list items
            formatted_players_items.append(
                " " * (indent_level * 2) + json.dumps(player_obj)
            )

        # Construct the "players" array string manually
        # The opening bracket needs indent_level (4 spaces)
        # Each item needs indent_level * 2 (8 spaces)
        # The closing bracket needs indent_level (4 spaces)
        players_string = (
            "[\n"
            + ",\n".join(formatted_players_items)
            + "\n"
            + " " * indent_level
            + "]"
        )

        # Replace the original list with a placeholder that we'll substitute later.
        # We'll use a unique string that won't naturally appear in JSON.
        placeholder = "__CUSTOM_PLAYERS_LIST_PLACEHOLDER__"
        data_copy[players_key] = placeholder

        # Dump the rest of the dictionary with standard indent=4
        json_output = json.dumps(data_copy, indent=indent_level)

        # Substitute the placeholder with our custom-formatted players string
        json_output = json_output.replace(f'"{placeholder}"', players_string)
    else:
        # If no players key or not a list, just dump normally
        json_output = json.dumps(data_copy, indent=indent_level)

    return json_output


def save_dict_with_pre_formatted_values(data_dict, filename, formatter_func):
    """
    Saves a dictionary to a file. Each value is assumed to be pre-formatted
    into a JSON string by the formatter_func.

    Args:
        data_dict (dict): The dictionary to save.
        filename (str): The name of the file to save the dictionary to.
        formatter_func (callable): A function that takes a value and returns
                                   its formatted JSON string representation.
    """
    processed_data = {}
    for key, value in data_dict.items():
        # Your formatter_func already returns a JSON string.
        # json.dump will treat this as a regular Python string,
        # and therefore, it will escape any internal quotes.
        processed_data[key] = formatter_func(value)

    try:
        with open(filename, "w") as f:
            # json.dump will write the Python strings (which are your JSON strings)
            # to the file. It will escape internal double quotes.
            json.dump(processed_data, f, indent=4)
        print(f"Dictionary successfully saved to {filename}")
    except IOError as e:
        print(f"Error saving dictionary to file: {e}")


@dataclass
class BotState:
    def __init__(self):
        os.makedirs("state", exist_ok=True)

    def backup(self):
        with open("state/backup.json", "w") as backup:
            mogi_registry = mogi_manager.read_registry()
            """ mogi_dicts = {
                id: mogi_registry[id].to_json() for id in mogi_registry.keys()
            }
            backup.write(pretty_encode_mogis(mogi_dicts)) """
            json.dump(
                {id: mogi_registry[id].to_json() for id in mogi_registry.keys()},
                backup,
                indent=4,
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
