from bson.int64 import Int64

from enum import Enum

from dataclasses import dataclass
from models.PlayerModel import PlayerProfile
from models.MogiModel import Mogi

from utils.data._database import db_players, db_archived, db_mogis


@dataclass
class DataManager:
    def __init__(self):
        pass

    class archive_type(Enum):
        NONE = "none"
        INCLUDE = "include"
        ONLY = "only"

    class sort_type(Enum):
        MMR = "MMR"
        WINS = "Wins"
        LOSSES = "Losses"
        WINRATE = "Winrate %"

    def find_player(
        query: int | Int64 | str, archive: archive_type = archive_type.NONE
    ) -> PlayerProfile | None:
        pass

    def get_all_players(
        archive: archive_type = archive_type.NONE,
    ) -> list[PlayerProfile] | None:
        pass

    def get_leaderboard(
        page_index: int, sort: sort_type = sort_type.MMR
    ) -> list[dict] | None:
        total_player_count = db_players.count_documents({})

        page_index = page_index if page_index > 0 else 1
        max_pages = -(-total_player_count // 10)

        page_index = page_index if page_index <= max_pages else max_pages

        skip_count = 10 * (page_index - 1)
        skip_count = (
            skip_count if skip_count < total_player_count else total_player_count - 10
        )
        skip_count = skip_count if skip_count >= 0 else 0

        pipeline = []

        # Add fields for Wins and Losses directly to the query results
        pipeline.append(
            {
                "$project": {
                    "name": 1,
                    "mmr": 1,
                    "history": 1,
                    "Wins": {
                        "$size": {
                            "$filter": {
                                "input": "$history",
                                "as": "delta",
                                "cond": {"$gte": ["$$delta", 0]},
                            }
                        }
                    },
                    "Losses": {
                        "$size": {
                            "$filter": {
                                "input": "$history",
                                "as": "delta",
                                "cond": {"$lt": ["$$delta", 0]},
                            }
                        }
                    },
                }
            }
        )

        # Calculate winrate
        pipeline.append(
            {
                "$addFields": {
                    "Winrate %": {
                        "$cond": [
                            {"$eq": [{"$add": ["$Wins", "$Losses"]}, 0]},
                            0,
                            {
                                "$multiply": [
                                    {
                                        "$divide": [
                                            "$Wins",
                                            {"$add": ["$Wins", "$Losses"]},
                                        ]
                                    },
                                    100,
                                ]
                            },
                        ]
                    }
                }
            }
        )

        sort_field = "mmr" if sort.value == "MMR" else sort.value
        pipeline.append({"$sort": {sort_field: -1}})

        pipeline.append({"$skip": skip_count})
        pipeline.append({"$limit": 10})

        return list(db_players.aggregate(pipeline))

    def delete_player(query: int | Int64 | str):
        pass


data_manager = DataManager({})
