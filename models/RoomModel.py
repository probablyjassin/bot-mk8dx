from dataclasses import dataclass


@dataclass
class Room:
    address: str
    description: str
    externalGuid: str
    hasPassword: bool
    id: str
    maxPlayers: int
    name: str
    netVersion: int
    owner: str
    players: list[dict]
    port: int
    preferredGameId: int
    preferredGameName: str

    def most_popular_game(self) -> tuple[int, str] | None:
        game_count = {}
        for player in self.players:
            game_name = player["gameName"]
            if game_name in game_count:
                game_count[game_name] += 1
            else:
                game_count[game_name] = 1
        most_popular = max(game_count, key=game_count.get)
        return (game_count[most_popular], most_popular) if game_count else None
