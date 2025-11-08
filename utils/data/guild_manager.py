from dataclasses import dataclass
from models.GuildModel import Guild, PlayingGuild
from models.PlayerModel import PlayerProfile
from utils.data.data_manager import data_manager


@dataclass
class GuildManager:
    def __init__(self):
        self.queue: dict[str, list[int]] = None
        self.playing_guilds: list[PlayingGuild] = None
        self.guilds_format: int | None = None
        self.placements: list[int] | None = None
        self.results: list[int] | None = None

    def queue_up(self, guild: Guild, player_id: int) -> None:
        if player_id not in guild.player_ids:
            raise ValueError("That player is not in that guild.")
        if guild.name in self.queue:
            self.queue[guild.name].append(player_id)
        else:
            self.queue[guild.name] = [player_id]

    def queue_drop(self, player_id: int) -> None:
        player_found = False
        for arr in self.queue.values():
            if player_id in arr:
                arr.remove(player_id)
                player_found = True
                break

        if not player_found:
            raise ValueError("That player is not in any queue.")

    async def start(self) -> tuple[int, list[PlayingGuild]]:
        queue = self.read_queue()
        min_players = max(len(min(list(queue.values()), key=len)), 2)

        for guild_name, player_id_list in queue.items():
            if len(queue[guild_name]) < 2:
                continue

            guild_obj = await data_manager.Guilds.find(guild_name)

            queued_players: list[PlayerProfile] = await data_manager.Players.find_list(
                player_id_list
            )

            playing_players: list[PlayerProfile] = queued_players[:min_players]
            subs: list[PlayerProfile] = queued_players[min_players:]

            playing_guild = PlayingGuild(
                guild=guild_obj, playing=playing_players, subs=subs
            )

            self.playing_guilds.append(playing_guild)

        self.guilds_format = min_players
        return min_players, self.playing_guilds

    def clear_queue(self) -> None:
        self.queue = {}
        self.playing_guilds = []
        self.guilds_format = None

    def clear_playing(self) -> None:
        self.playing_guilds = []
        self.guilds_format = None

    def read_queue(self) -> dict[str, list[int]]:
        return self.queue

    def read_playing(self) -> list[PlayingGuild]:
        return self.playing_guilds

    def write_registry(self, data: dict) -> None:
        self.queue = data.get("queue", {})

        # Deserialize playing_guilds from JSON
        playing_guilds_data: list[dict] = data.get("playing_guilds", [])
        self.playing_guilds = [
            PlayingGuild.from_json(pg_data) for pg_data in playing_guilds_data
        ]

        self.guilds_format = data.get("guilds_format")
        self.placements = data.get("placements")
        self.results = data.get("results")

    def read_registry(self) -> dict:
        return {
            "queue": self.queue,
            "playing_guilds": (
                [pg.to_json_full() for pg in self.playing_guilds]
                if self.playing_guilds
                else []
            ),
            "guilds_format": self.guilds_format,
            "placements": self.placements,
            "results": self.results,
        }


guild_manager = GuildManager()
