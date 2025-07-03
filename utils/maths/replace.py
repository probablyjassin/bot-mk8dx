from models.PlayerModel import PlayerProfile


def recurse_replace(
    space: list | list[list] | PlayerProfile, player: PlayerProfile, sub: PlayerProfile
):
    if isinstance(space, list):
        return [recurse_replace(item, player, sub) for item in space]
    elif hasattr(space, "discord_id") and hasattr(player, "discord_id"):
        return sub if space.discord_id == player.discord_id else space
