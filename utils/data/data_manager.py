from pymongo import UpdateOne
from bson.int64 import Int64

from enum import Enum

from dataclasses import dataclass
from models.PlayerModel import PlayerProfile
from models.MogiModel import MogiHistoryData

from utils.data._database import db_players, db_mogis


class archive_type(Enum):
    NO = {"inactive": {"$ne": True}}
    INCLUDE = {}
    ONLY = {"inactive": True}


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
        self,
        query: int | Int64 | str,
        archive: archive_type = archive_type.NO,
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
                },
                archive.value,
            ]
        }

        potential_player = next(
            db_players.aggregate([{"$match": query_criteria}, {"$limit": 1}]), None
        )

        return PlayerProfile(**potential_player) if potential_player else None

    def get_all_player_profiles(
        self,
        archive: archive_type = archive_type.NO,
        with_id: bool = False,
    ) -> list[PlayerProfile] | list[dict] | None:
        return [
            PlayerProfile.from_json(player)
            for player in list(
                db_players.find(archive.value, {"_id": 0} if not with_id else {})
            )
        ]

    def get_all_player_entries(
        self,
        archive: archive_type = archive_type.NO,
        with_id: bool = False,
    ) -> list[dict] | None:
        return list(db_players.find(archive.value, {"_id": 0} if not with_id else {}))

    def create_new_player(self, username: str, discord_id: int, join_time: int) -> None:
        db_players.insert_one(
            {
                "name": username,
                "discord_id": Int64(discord_id),
                "mmr": 2000,
                "history": [],
                "joined": join_time,
            },
        )

    def get_leaderboard(
        self, page_index: int, sort: sort_type = sort_type.MMR
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

    def delete_player(self, query: int | Int64 | str):
        pass

    def get_all_mogis(self, with_id: bool = False) -> list[MogiHistoryData]:
        return [
            MogiHistoryData.from_dict(mogi)
            for mogi in list(db_mogis.find({}, {"_id": 0} if not with_id else {}))
        ]

    def get_all_mogi_entries(self, with_id: bool = False) -> list[dict]:
        return list(db_mogis.find({}, {"_id": 0} if not with_id else {}))

    def add_mogi_history(
        self,
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

    def apply_result_mmr(self, usernames: list[str], deltas: list[int]) -> None:
        """
        ### Apply MMR results to players
        Note: Subs need to be removed prior from this list, the function does not check for this.
        """
        db_players.bulk_write(
            [
                UpdateOne(
                    {"name": entry["name"]},
                    {
                        "$set": {
                            "mmr": {"$max": [1, {"$add": ["$mmr", entry["delta"]]}]}
                        },
                        "$push": {"history": entry["delta"]},
                    },
                    upsert=False,
                )
                for entry in (
                    {"name": usernames[i], "delta": deltas[i]}
                    for i in range(len(usernames))
                )
            ]
        )

    def bulk_add_mmr(self, player_usernames: list[str], amount: int) -> None:
        """
        ### Add a certain `amount` of MMR to every player (by username) provided.
        `amount` may be negative\n
        It's ensured each player's MMR is still 1 or more total.
        """
        db_players.bulk_write(
            [
                UpdateOne(
                    {"name": username},
                    [
                        {
                            "$set": {
                                "mmr": {"$max": [1, {"$add": ["$mmr", amount]}]},
                            },
                            "$push": {"history": amount},
                        }
                    ],
                    upsert=False,
                )
                for username in player_usernames
            ]
        )


data_manager = DataManager()
