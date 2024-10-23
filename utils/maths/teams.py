from models.PlayerModel import PlayerProfile

def distribute_players_to_teams(players_in_mogi: list[PlayerProfile], team_size: int) -> list[list[PlayerProfile]]:
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
