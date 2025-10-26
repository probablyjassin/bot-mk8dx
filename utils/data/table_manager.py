import os
from discord import Attachment
from dataclasses import dataclass
from models import Mogi


@dataclass
class TableManager:
    def __init__(self):
        self.ss_dir = "state/screenshots"
        os.makedirs(self.ss_dir, exist_ok=True)

    async def save_screenshot(
        self, mogi: Mogi, image: Attachment, races: int, total: int
    ) -> None:
        os.makedirs(f"{self.ss_dir}/{mogi.channel_id}", exist_ok=True)
        filename = f"ss.{races}_races.{total}.png"
        filepath = f"{self.ss_dir}/{mogi.channel_id}/{filename}"

        with open(filepath, "wb") as f:
            f.write(await image.read())


table_manager = TableManager({})
