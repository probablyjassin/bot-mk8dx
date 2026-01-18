from ._mongodb import db_players
from database.types import archive_type, sort_type


async def get_leaderboard(
    page_index: int,
    sort: sort_type = sort_type.MMR,
    archive: archive_type = archive_type.NO,
) -> list[dict] | None:
    total_player_count = await db_players.count_documents({})

    page_index = page_index if page_index > 0 else 1
    max_pages = -(-total_player_count // 10)

    page_index = page_index if page_index <= max_pages else max_pages

    skip_count = 10 * (page_index - 1)
    skip_count = (
        skip_count if skip_count < total_player_count else total_player_count - 10
    )
    skip_count = skip_count if skip_count >= 0 else 0

    pipeline = []

    # Add match stage to filter players
    filter = {
        "inactive": {"$ne": True},
        "history": {"$exists": True, "$not": {"$size": 0}},
    }
    if archive == archive_type.NO:
        filter["archived"] = {"$ne": True}
    if archive == archive_type.ONLY:
        filter["archived"] = True

    pipeline.append({"$match": filter})

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

    return await db_players.aggregate(pipeline).to_list(length=None)
