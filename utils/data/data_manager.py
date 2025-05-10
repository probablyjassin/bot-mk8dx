from bson.int64 import Int64

from enum import Enum

from dataclasses import dataclass
from models.PlayerModel import PlayerProfile
from models.MogiModel import MogiHistoryData

from utils.data._database import db_players, db_archived, db_mogis


class archive_type(Enum):
    NONE = "none"
    INCLUDE = "include"
    ONLY = "only"


class sort_type(Enum):
    MMR = "MMR"
    WINS = "Wins"
    LOSSES = "Losses"
    WINRATE = "Winrate %"


@dataclass
class DataManager:
    def __init__(self):
        pass

    def find_player(
        query: int | Int64 | str, archive: archive_type = archive_type.NONE
    ) -> PlayerProfile | None:
        query_criteria = {
            "$and": [
                {
                    "$or": [
                        {"name": (query.lower() if isinstance(query, str) else query)},
                        {
                            "discord_id": (
                                Int64(query)
                                if isinstance(query, Int64 | int)
                                else (
                                    Int64(query.strip("<@!>"))
                                    if query.strip("<@!>").isdigit()
                                    else None
                                )
                            )
                        },
                    ]
                }
            ]
        }

        if archive == archive_type.NONE:
            query_criteria["$and"].append({"inactive": {"$ne": True}})
        if archive == archive_type.ONLY:
            query_criteria["$and"].append({"inactive": True})

        potential_player = next(
            db_players.aggregate({"$match": query_criteria}, {"$limit": 1}), None
        )

        return PlayerProfile(**potential_player) if potential_player else None

    def get_all_players(
        archive: archive_type = archive_type.NONE, with_id: bool = False
    ) -> list[PlayerProfile] | None:
        return [
            PlayerProfile.from_json(player)
            for player in list(db_players.find({}, {"_id": 0} if with_id else {}))
        ]

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

        # Add match stage to filter out inactive players
        pipeline.append(
            {
                "$match": {
                    "inactive": {"$ne": True},
                    "history": {"$exists": True, "$not": {"$size": 0}},
                }
            }
        )

        # Add fields for Wins and Losses directly to the query results
        pipeline.append(
            {
                "$project": {
                    "_id": 0,
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

    def get_all_mogis(with_id: bool = False) -> list[MogiHistoryData]:
        return [
            MogiHistoryData.from_dict(mogi)
            for mogi in list(db_mogis.find({}, {"_id": 0} if with_id else {}))
        ]

    def add_mogi_history(
        started_at: int,
        finished_at: int,
        player_ids: list[int],
        format: int,
        subs: int,
        results: list[int],
        disconnections: int,
    ) -> None:
        db_mogis.insert_one(
            {
                "started_at": started_at,
                "finished_at": finished_at,
                "player_ids": player_ids,
                "format": format,
                "subs": subs,
                "results": results,
                "disconnections": disconnections,
            }
        )


data_manager = DataManager({})
