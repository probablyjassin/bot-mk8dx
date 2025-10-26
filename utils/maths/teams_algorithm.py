import os
import importlib.util
import random
from models import PlayerProfile


def teams_alg_distribute_by_order_kevnkkm(
    players_in_mogi: list[PlayerProfile], team_size: int
) -> list[list[PlayerProfile]]:
    """
    Distribute players to teams in a balanced fashion based on their MMR (using greedy approach).

    :param players_in_mogi: Array of the players in the mogi.
    :param team_size: Number of players per team.
    :return: List of teams with distributed players.
    """
    # Sort players by MMR in descending order
    player_count = len(players_in_mogi)
    team_count = player_count // team_size

    players_in_mogi.sort(key=lambda player: player.mmr, reverse=True)

    # Initialize teams
    teams = [[] for _ in range(team_count)]

    reverse = False
    team_index = 0

    for i in range(player_count):
        teams[team_index].append(players_in_mogi[i])

        if not reverse:
            team_index += 1
            if team_index == team_count:
                team_index -= 1
                reverse = True
        else:
            team_index -= 1
            if team_index == -1:
                team_index += 1
                reverse = False

    return teams


def teams_alg_random(
    players_in_mogi: list[PlayerProfile], team_size: int
) -> list[list[PlayerProfile]]:
    """
    Randomly distribute players to teams.\n
    Literally just randomness.\n
    Why are you still reading this docstring, there's nothing to it.\n
    Look, I'll show you the code right here cuz it's that short:\n
    `random_players = random.shuffle(players_in_mogi)` \n
    `return [random_players[i:i + team_size] for i in range(0, len(random_players), team_size)]`

    :param players_in_mogi: Array of the players in the mogi.
    :param team_size: Number of players per team.
    :return: List of teams with distributed players.
    """
    players = players_in_mogi.copy()
    random.shuffle(players)
    return [players[i : i + team_size] for i in range(0, len(players), team_size)]


# if ever implemented
def get_other_alg():
    file_path = "other.py"
    function_name = "teams_alg_other"
    if os.path.exists(file_path):
        spec = importlib.util.spec_from_file_location("module.name", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, function_name):
            return getattr(module, function_name)
    return teams_alg_random
