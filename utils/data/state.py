import os
import json
from dataclasses import dataclass

from models.MogiModel import Mogi
from utils.data.mogi_manager import write_registry, mogi_registry


@dataclass
class BotState:
    def __init__(self):
        os.makedirs("state", exist_ok=True)

    def backup(self):
        with open("state/backup.json", "w") as backup:
            json.dump(
                {id: mogi_registry[id].to_dict() for id in mogi_registry.keys()},
                backup,
            )

    def save(self):
        with open("state/saved.json", "w") as saved:
            json.dump(
                {id: mogi_registry[id].to_dict() for id in mogi_registry.keys()},
                saved,
            )

    def load_backup(self):
        if not os.path.exists("state/backup.json"):
            return
        with open("state/backup.json", "r") as backup:
            data: dict = json.load(backup)
            if data:
                write_registry({id: Mogi.from_dict(data[id]) for id in data.keys()})
            else:
                print("No backup data found")

    def load_saved(self):
        if not os.path.exists("state/saved.json"):
            return
        with open("state/saved.json", "r") as saved:
            global mogi_registry
            data: dict = json.load(saved)
            if data:
                mogi_registry = data


state_manager = BotState()
