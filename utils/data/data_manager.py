from dataclasses import dataclass

from utils.database import players
from utils.database import aliases
from utils.database import leaderboard
from utils.database import mogis
from utils.database import guilds


@dataclass
class DataManager:
    class Players:
        find = staticmethod(players.find_player)
        create_new_player = staticmethod(players.create_new_player)
        get_profiles = staticmethod(players.get_profiles)
        get_all_player_names = staticmethod(players.get_all_player_names)
        count = staticmethod(players.count)
        set_attribute = staticmethod(players.set_attribute)
        append_history = staticmethod(players.append_history)
        count_format_played = staticmethod(players.count_format_played)
        delete = staticmethod(players.delete_player)

    class Aliases:
        set_player_alias = staticmethod(aliases.set_player_alias)
        get_all_aliases = staticmethod(aliases.get_all_aliases)

    class Leaderboard:
        get_leaderboard = staticmethod(leaderboard.get_leaderboard)

    class Mogis:
        get_all_mogis = staticmethod(mogis.get_all_mogis)
        add_mogi_history = staticmethod(mogis.add_mogi_history)
        apply_result_mmr = staticmethod(mogis.apply_result_mmr)
        bulk_add_mmr = staticmethod(mogis.bulk_add_mmr)

    class Guilds:
        find = staticmethod(guilds.find_guild)
        get_all_guilds = None
        get_all_guild_names = staticmethod(guilds.get_all_guild_names)
        create = staticmethod(guilds.create_new_guild)
        delete = staticmethod(guilds.delete_guild)
        add_member = staticmethod(guilds.add_member)
        remove_member = staticmethod(guilds.remove_member)
        player_has_guild = staticmethod(guilds.player_has_guild)
        get_player_guild = staticmethod(guilds.get_player_guild)
        append_history = staticmethod(guilds.append_history)
        set_attribute = staticmethod(guilds.set_attribute)


data_manager = DataManager()
