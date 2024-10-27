from dataclasses import dataclass, field

from discord import Interaction, WebhookMessage
from models.PlayerModel import PlayerProfile

from utils.maths.teams_algorithm import distribute_players_to_teams


@dataclass
class Mogi:
    """
    ### Represents a Mogi in a channel.
    """

    channel_id: int
    player_cap: int = 12
    format: int | None = None

    players: list[PlayerProfile] = field(default_factory=lambda: [])
    teams: list[list[PlayerProfile]] = field(default_factory=lambda: [])
    subs: list[PlayerProfile] = field(default_factory=lambda: [])

    isVoting: bool = False
    isPlaying: bool = False
    isFinished: bool = False

    collected_points: list[int] = field(default_factory=lambda: [])
    placements_by_group: list[int] = field(default_factory=lambda: [])
    mmr_results_by_group: list[int] = field(default_factory=lambda: [])

    voting_message: Interaction | WebhookMessage | None = None
    voters: list[int] = field(default_factory=lambda: [])
    votes: dict[str, int] = field(
        default_factory=lambda: {
            "ffa": 0,
            "2v2": 0,
            "3v3": 0,
            "4v4": 0,
            "6v6": 0,
        }
    )

    team_tags: list[str] = field(
        default_factory=lambda: [
            "Team 1",
            "Team 2",
            "Team 3",
            "Team 4",
            "Team 5",
            "Team 6",
        ]
    )

    def play(self, format_int: int) -> None:
        self.format = format_int

        if format_int == 1:
            for player in self.players:
                self.teams.append([player])

        else:
            self.teams = distribute_players_to_teams(self.players, format_int)
            # important: we put players in the new order determined by the team-making
            self.players = [player for team in self.teams for player in team]

        self.isVoting = False
        self.isPlaying = True

        self.voters = []
        self.votes = {key: 0 for key in self.votes}

    def stop(self) -> None:
        self.votes = {key: 0 for key in self.votes}
        self.voters.clear()
        self.isVoting = False
        self.isPlaying = False
        self.isFinished = False

    def collect_points(self, tablestring: str) -> None:
        all_points = {}

        for line in tablestring.split("\n"):
            for player in self.players:
                if player.name in line:
                    points = sum(
                        [
                            int(num)
                            for part in [part.split("+") for part in line.split()]
                            for num in part
                            if num.isdigit()
                        ]
                    )
                    all_points[player.name] = points

        team_points_list = []
        for team in self.teams:
            team_points = sum(all_points[player.name] for player in team)
            team_points_list.append(team_points)

        self.collected_points = team_points_list

    def finish(self) -> None:
        self.isPlaying = False
        self.isFinished = True
