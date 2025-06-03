import os
import json
from dataclasses import dataclass
from collections import OrderedDict

from models.MogiModel import Mogi
from utils.data.mogi_manager import mogi_manager


def pretty_encode_mogis(mogis_dict):
    class PlaceholderEncoder(json.JSONEncoder):
        def default(self, obj):
            if hasattr(obj, "to_json"):
                data = obj.to_json()
                ordered = OrderedDict()
                for key, value in data.items():
                    if key == "players":
                        ordered[key] = "__PLAYERS_PLACEHOLDER__"
                    else:
                        ordered[key] = value
                return ordered
            return super().default(obj)

    # First pass: serialize with placeholder
    json_str = json.dumps(
        {str(k): v for k, v in mogis_dict.items()}, cls=PlaceholderEncoder, indent=4
    )

    # Replace placeholders with compact player lists
    result_lines = []
    current_id = None

    for line in json_str.splitlines():
        stripped = line.strip()
        if stripped.endswith("{") and stripped.startswith('"') and ":" in stripped:
            # Example: "1180622895316209664": {
            current_id = stripped.split(":")[0].strip('"')

        if '"players": "__PLAYERS_PLACEHOLDER__"' in line:
            if current_id is None:
                raise ValueError("Could not determine current Mogi ID.")

            indent = line[: line.find('"players"')]
            mogi = mogis_dict[int(current_id)]
            players_compact = (
                "[\n"
                + ",\n".join(
                    [
                        indent + "    " + json.dumps(p.to_json(), separators=(",", ":"))
                        for p in mogi.players
                    ]
                )
                + f"\n{indent}]"
            )
            result_lines.append(f'{indent}"players": {players_compact},')
        else:
            result_lines.append(line)

    return "\n".join(result_lines)


@dataclass
class BotState:
    def __init__(self):
        os.makedirs("state", exist_ok=True)

    def backup(self):
        with open("state/backup.json", "w") as backup:
            mogis = mogi_manager.read_registry()
            backup.write(
                pretty_encode_mogis({id: mogis[id].to_json() for id in mogis.keys()})
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
        if not os.path.exists("state/backup.json"):
            return
        with open("state/backup.json", "r") as backup:
            data: dict = json.load(backup)
            if data:
                mogi_manager.write_registry(
                    {int(id): Mogi.from_json(data[id]) for id in data.keys()}
                )
            else:
                print("No backup data found")

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
