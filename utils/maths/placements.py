def get_placements_from_scores(points: dict[str, int]) -> dict[str, int]:
    """
    Returns a list of placements from a list of scores.

    Args:
    - scores (list[tuple[int, int]]): A list of scores where each score is a tuple of (player_id, score).

    Returns:
    - list[int]: A list of placements for each player in the scores list.
    """
    ranks_dict: dict[str, int] = {}
    for i, score in enumerate(sorted(points, reverse=True)):
        if score[0] not in ranks_dict:
            ranks_dict[score[0]] = i + 1
    return {player: ranks_dict[player] for player in points}
