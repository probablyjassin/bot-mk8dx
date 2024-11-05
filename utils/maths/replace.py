from models import PlayerProfile


def recurse_replace(
    space: list | list[list], player: PlayerProfile, sub: PlayerProfile
):
    if isinstance(space, list):
        return [recurse_replace(item, player, sub) for item in space]
    else:
        return sub if space == player else space
