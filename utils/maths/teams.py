from utils.mogis import get_mogi

# INFO: @Jässin, this should be done for the most part but we need to see how the method gets called in the first place.
# That could change the arguments that need to be passed in for example.

def distribute_players_to_teams(channel_id: int, team_size: int) -> list[list[PlayerProfile]]:
    """
    Distribute players to teams in a balanced fashion based on their MMR (using greedy approach).

    :param channel_id: ID of the channel to get the player list from.
    :param team_size: Number of players per team.
    :return: List of teams with distributed players.
    """
    # Sort players by MMR in descending order
    player_list = get_mogi(channel_id).players
    player_count = len(player_list)
    team_count = player_count // team_size

    player_list.sort(key=lambda player: player.mmr, reverse=True)

    # Initialize teams
    teams = [[] for _ in range(team_count)]

    reverse = False
    team_index = 0

    for i in range(player_count):
        teams[team_index].append(player_list[i])

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
