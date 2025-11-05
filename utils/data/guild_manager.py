from dataclasses import dataclass
from models.GuildModel import Guild


@dataclass
class GuildManager:
    def __init__(self, data: dict[str, list]):
        self._guild_mogi_registry = data

    _guild_mogi_registry: dict[str, list[int]]

    def queue_up(self, guild: Guild, player_id: int) -> None:
        if player_id not in guild.player_ids:
            raise ValueError("That player is not in that guild.")
        if guild.name in self._guild_mogi_registry:
            self._guild_mogi_registry[guild.name].append(player_id)
        else:
            self._guild_mogi_registry[guild.name] = [player_id]

    def queue_drop(self, player_id: int) -> None:
        player_found = False
        for arr in self._guild_mogi_registry.values():
            if player_id in arr:
                arr.remove(player_id)
                player_found = True
                break

        if not player_found:
            raise ValueError("That player is not in any queue.")

    def write_registry(self, data: dict[str, list]) -> None:
        self._guild_mogi_registry = data

    def read_registry(self) -> dict[str, list]:
        return self._guild_mogi_registry


guild_manager = GuildManager({})
