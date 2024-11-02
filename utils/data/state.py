import os
import json
from dataclasses import dataclass

from models.MogiModel import Mogi
from utils.data.mogi_manager import mogi_manager


@dataclass
class BotState:
    def __init__(self):
        os.makedirs("state", exist_ok=True)

    def backup(self):
        with open("state/backup.json", "w") as backup:
            mogis = mogi_manager.read_registry()
            json.dump(
                {id: mogis[id].to_json() for id in mogis.keys()},
                backup,
            )

    def save(self):
        with open("state/saved.json", "w") as saved:
            mogis = mogi_manager.read_registry()
            json.dump(
                {id: mogis[id].to_json() for id in mogis.keys()},
                saved,
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
