import time
from dataclasses import dataclass, field
from bson import ObjectId

from models.PlayerModel import PlayerProfile
from models.RoomModel import Room

from utils.data._database import db_mogis
from utils.maths.teams_algorithm import (
    teams_alg_distribute_by_order_kevnkkm,
    teams_alg_random,
)

from utils.data.flags import debug_feature_flags


@dataclass
class Mogi:
    """
    ### Represents a Mogi in a discord channel.
    #### Attributes:
        channel_id (`int`): Integer ID of the channel where the Mogi lives.
        format (`int | None`): Integer representing the format of the Mogi (e.g., FFA, 2v2, etc.). Is `None` when the mogi hasn't started.
        room (`Room | None`): NOT_IMPLEMENTED_YET: Room object representing the Yuzu Server the mogi is played on. Is `None` when the mogi hasn't started.
        players (`list[PlayerProfile]`): List of player profiles participating in the Mogi.
        teams (`list[list[PlayerProfile]]`): List of List for every team with their players. In FFA, each sublist has only one player.
        subs (`list[PlayerProfile]`): A list of those players who are playing as sub for someone else.
        isVoting (`bool`): Indicates if voting is currently active. Default is False.
        isPlaying (`bool`): Indicates if the mogi is currently in progress (playing the races). Default is False.
        isFinished (`bool`): Indicates if the mmr calculation has finished. Default is False.
        collected_points (`list[int]`): A list of points collected in order of each team/player.
        placements_by_group (`list[int]`): A list of placements in order of teams/players.
        mmr_results_by_group (`list[int]`): A list of MMR results in order of teams/players.
        voting_message_id (`int | None`): The ID of the message that has the voting. Stored to be able to delete it if /stop is used. Default is None.
        table_message_id (`int | None`): The ID of the message that has the table. Stored to be able to delete it if /points reset is used. Default is None.
        voters (`list[int]`): A list of the discord IDs of those players who have voted for a format.
        votes (`dict[str, int]`): A dictionary of the number of votes each format got.
        team_tags (`list[str]`): A list of team tags.
        player_cap (`int`): FOR TESTING ONLY: The maximum number of players allowed in the Mogi. Default is 12.
    Methods:
        play(format_int: `int`) -> `None`:
            Starts the mogi with the given format. If the format is teams, assigns players to teams.
        stop() -> None:
            Stops the current game, resets voting and game states.
        collect_points(tablestring: `str`) -> `None`:
            Collects points from a given table string and updates the collected points for each team.
        finish() -> `None`:
            Marks the game as finished, updating the game state.
    """

    channel_id: int
    player_cap: int = 12
    format: int | None = None
    room: Room | None = None

    players: list[PlayerProfile] = field(default_factory=lambda: [])
    teams: list[list[PlayerProfile]] = field(default_factory=lambda: [])
    subs: list[PlayerProfile] = field(default_factory=lambda: [])

    isVoting: bool = False
    isPlaying: bool = False
    isFinished: bool = False

    collected_points: list[int] = field(default_factory=lambda: [])
    placements_by_group: list[int] = field(default_factory=lambda: [])
    mmr_results_by_group: list[int] = field(default_factory=lambda: [])
    table_message_id: int | None = None

    voting_message_id: int | None = None
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

    started_at: int | None = None
    finished_at: int | None = None
    disconnections: int | None = 0

    def play(self, format_int: int) -> None:
        """
        ### Organizes players into teams and updates the game state based on the given format.
        #### Parameters:
        format_int (int): An integer representing the format of the game.
                          If format_int is 1, each player is placed in their own team.
                          Otherwise, players are distributed into teams based on the format.
        #### Side Effects:
        - Updates the `self.format` attribute with the given format.
        - Modifies the `self.teams` attribute to contain the new teams.
        - Reorders `self.players` based on the new team assignments.
        - Sets `self.isVoting` to False.
        - Sets `self.isPlaying` to True.
        - Resets `self.voters` to an empty list.
        - Resets the vote counts in `self.votes` to 0.

        """
        self.format = format_int

        if format_int == 1:
            for player in self.players:
                self.teams.append([player])

        else:
            algorithm = (
                teams_alg_random
                if debug_feature_flags["random_teams"]
                else teams_alg_distribute_by_order_kevnkkm
            )
            self.teams = algorithm(self.players, format_int)
            # important: we put players in the new order determined by the team-making
            self.players = [player for team in self.teams for player in team]

        self.isVoting = False
        self.isPlaying = True
        self.started_at = round(time.time())

        self.voters = []
        self.votes = {key: 0 for key in self.votes}

    def stop(self) -> None:
        """
        Stops the current process and resets the voting and playing states.
        This method performs the following actions:
        - Resets all votes to zero.
        - Clears the list of voters.
        - Sets the voting state to False.
        - Sets the playing state to False.
        - Sets the finished state to False.
        """

        self.votes = {key: 0 for key in self.votes}
        self.voters.clear()
        self.isVoting = False
        self.isPlaying = False
        self.format = None
        self.teams.clear()

        self.isFinished = False
        self.started_at = None

    def collect_points(self, tablestring: str) -> None:
        """
        Collects and calculates points for players and teams from a given table string.
        Args:
            tablestring (`str`): The string obtained from `/l context:table`
        """

        all_points = {}

        try:
            for line in tablestring.split("\n"):
                line = line.replace("|", "+")
                sections = line.split()
                for player in self.players:
                    if sections and sections[0] == player.name:
                        parts = [part.split("+") for part in line.split()]
                        points = sum(
                            [
                                int(num)
                                for part in parts
                                for num in part
                                if num.isdigit()
                            ]
                        )
                        all_points[player.name] = points
                        self.disconnections = (
                            len(
                                [num for part in parts for num in part if num.isdigit()]
                            )
                            - 1
                        )
        except Exception as e:
            print(
                "Defaulted to old tablestring collect_points method because of errors"
            )
            print(e)
            all_points = {}
            self.disconnections = 0
            for line in tablestring.split("\n"):
                line = line.replace("|", "+")
                for player in self.players:
                    if player.name in line:
                        parts = [part.split("+") for part in line.split()]
                        points = sum(
                            [
                                int(num)
                                for part in parts
                                for num in part
                                if num.isdigit()
                            ]
                        )
                        all_points[player.name] = points
                        self.disconnections = (
                            len(
                                [num for part in parts for num in part if num.isdigit()]
                            )
                            - 1
                        )

        team_points_list = []
        for team in self.teams:

            try:
                team_points = sum(all_points[player.name] for player in team)
            except KeyError as error:
                raise error

            team_points_list.append(team_points)

        self.collected_points = team_points_list

    def archive_mogi_data(self) -> None:
        """
        Save the mogi to the database.
        """
        db_mogis.insert_one(
            {
                "started_at": self.started_at,
                "finished_at": self.finished_at,
                "player_ids": [player.discord_id for player in self.players],
                "format": self.format,
                "subs": len(self.subs),
                "results": self.mmr_results_by_group,
                "disconnections": self.disconnections,
            }
        )

    def finish(self) -> None:
        """
        Marks the current mogi as completed.
        #### Side Effects:
        - Sets `self.isPlaying` to False.
        - Sets `self.isFinished` to True.
        """

        self.isPlaying = False
        self.isFinished = True
        self.finished_at = round(time.time())
        self.archive_mogi_data()

    def to_json(self) -> dict:
        """
        Converts the Mogi instance to a dictionary.
        Returns:
            dict: A dictionary representation of the Mogi instance.
        """
        return {
            "channel_id": self.channel_id,
            "player_cap": self.player_cap,
            "format": self.format,
            "room": self.room.to_json() if self.room else None,
            "players": [player.to_json() for player in self.players],
            "teams": [[player.to_json() for player in team] for team in self.teams],
            "subs": [sub.to_json() for sub in self.subs],
            "isVoting": self.isVoting,
            "isPlaying": self.isPlaying,
            "isFinished": self.isFinished,
            "collected_points": self.collected_points,
            "placements_by_group": self.placements_by_group,
            "mmr_results_by_group": self.mmr_results_by_group,
            "voting_message_id": self.voting_message_id,
            "voters": self.voters,
            "votes": self.votes,
            "team_tags": self.team_tags,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "disconnections": self.disconnections,
        }

    @classmethod
    def from_json(cls, data: dict) -> "Mogi":
        """
        Creates a Mogi instance from a dictionary.
        Args:
            data (dict): A dictionary representation of a Mogi instance.
        Returns:
            Mogi: A Mogi instance created from the dictionary.
        """
        return cls(
            channel_id=data["channel_id"],
            player_cap=data.get("player_cap", 12),
            format=data.get("format"),
            room=Room.from_json(data.get("room", None)),
            players=[
                PlayerProfile.from_json(player) for player in data.get("players", [])
            ],
            teams=[
                [PlayerProfile.from_json(player) for player in team]
                for team in data.get("teams", [])
            ],
            subs=[PlayerProfile.from_json(sub) for sub in data.get("subs", [])],
            isVoting=data.get("isVoting", False),
            isPlaying=data.get("isPlaying", False),
            isFinished=data.get("isFinished", False),
            collected_points=data.get("collected_points", []),
            placements_by_group=data.get("placements_by_group", []),
            mmr_results_by_group=data.get("mmr_results_by_group", []),
            voting_message_id=data.get("voting_message_id"),
            voters=data.get("voters", []),
            votes=data.get("votes", {"ffa": 0, "2v2": 0, "3v3": 0, "4v4": 0, "6v6": 0}),
            team_tags=data.get(
                "team_tags",
                ["Team 1", "Team 2", "Team 3", "Team 4", "Team 5", "Team 6"],
            ),
            started_at=data.get("started_at"),
            finished_at=data.get("finished_at"),
            disconnections=data.get("disconnections", 0),
        )


@dataclass
class MogiHistoryData:
    started_at: int
    finished_at: int
    player_ids: list[int]
    format: int
    subs: int
    results: list[int]
    disconnections: int
    _id: ObjectId = field(default_factory=lambda: ObjectId())

    @classmethod
    def from_dict(cls, data: dict) -> "MogiHistoryData":
        return cls(
            _id=ObjectId(data["_id"]),
            started_at=data["started_at"],
            finished_at=data["finished_at"],
            player_ids=data["player_ids"],
            format=data["format"],
            subs=data["subs"],
            results=data["results"],
            disconnections=data["disconnections"],
        )
