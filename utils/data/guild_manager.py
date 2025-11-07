from dataclasses import dataclass
from models.GuildModel import Guild


@dataclass
class GuildManager:
    def __init__(self, data: dict[str, list]):
        self._guild_mogi_registry: dict[str, list] = data
        self.playing_guilds: list[str] = []
        self.guilds_format: int | None = None

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

    def start(self) -> tuple[int, list[str]]:
        queue = self.read_queue()
        min_players = 12
        for guild_name in queue:
            if len(queue[guild_name]) < 2:
                continue
            self.playing_guilds.append(guild_name)
            min_players = min(min_players, len(queue[guild_name]))
        self.guilds_format = min_players
        return min_players, self.playing_guilds

    def clear_queue(self) -> None:
        self._guild_mogi_registry = {}
        self.playing_guilds = []
        self.guilds_format = None

    def clear_playing(self) -> None:
        self.playing_guilds = []
        self.guilds_format = None

    def read_queue(self) -> dict[str, list[int]]:
        return self._guild_mogi_registry

    def read_playing(self) -> list[str]:
        return self.playing_guilds

    def write_registry(self, data: dict[str, list]) -> None:
        self._guild_mogi_registry = data

    def read_registry(self) -> dict[str, list]:
        return self._guild_mogi_registry


guild_manager = GuildManager({})
