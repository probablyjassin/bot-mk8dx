import requests
from io import BufferedReader
from config import TABLE_READER_URL
from typing import TypedDict, cast
from fuzzywuzzy import process
from config import player_name_aliases


class OCRPlayerList(TypedDict):
    position: int
    name: str
    score: str


def table_read_ocr_api(file: BufferedReader) -> list[OCRPlayerList]:
    """
    Send a buffered binary file to the table reader API and return the JSON response.
    """
    try:
        file.seek(0)
    except Exception:
        pass

    response = requests.post(TABLE_READER_URL, files={"file": file}, timeout=30)
    response.raise_for_status()

    data = response.json()
    if not data["players"]:
        return None

    return cast(OCRPlayerList, response.json()["players"])


def ocr_to_tablestring(ocr_names: list[str], scores: list[str]) -> str:
    tablestring = "-\n"
    for i, name in enumerate(ocr_names):
        tablestring += f"{name} {scores[i]}+\n\n"
    return tablestring


def pattern_match_lounge_names(
    players: list[str], lounge_names: list[str]
) -> list[str] | None:
    actual_names = players[:]

    print("--- thingy matching results: ----")
    for i, name in enumerate(players):
        # search by lounge name
        match_result: tuple[str, int] | None = process.extractOne(name, lounge_names)
        if match_result is None:
            print(f"failed to match {name}")
            return None
        print(match_result)
        candidate_name, _ = match_result
        actual_names[i] = candidate_name

        # search by given aliases
        potential_alias_match, certainty = process.extractOne(
            name, list(player_name_aliases.values())
        )
        if potential_alias_match and certainty > 70:
            actual_names[i] = player_name_aliases.keys()[
                list(player_name_aliases.values()).index(potential_alias_match)
            ]

    return actual_names
