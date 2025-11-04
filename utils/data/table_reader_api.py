from io import BufferedReader
import requests
from typing import TypedDict, cast
from fuzzywuzzy import process

from utils.data import data_manager
from config import TABLE_READER_URL


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
    actual_names = [None] * len(players)
    available_lounge_names = lounge_names[:]

    print("--- thingy matching results: ----")

    # Pass 1: lock in high-confidence matches (>90 score)
    for i, name in enumerate(players):
        match_result: tuple[str, int] | None = process.extractOne(
            name, available_lounge_names
        )
        if match_result is None:
            print(f"failed to match {name}")
            return None
        candidate_name, score = match_result
        if score > 90:
            actual_names[i] = candidate_name
            available_lounge_names.remove(candidate_name)
            print(f"High confidence: {name} → {candidate_name} ({score})")

    # Pass 2: match remaining players from remaining pool
    for i, name in enumerate(players):
        if actual_names[i] is not None:
            continue  # already matched

        match_result: tuple[str, int] | None = process.extractOne(
            name, available_lounge_names
        )
        if match_result is None:
            print(f"failed to match {name}")
            return None
        candidate_name, score = match_result
        actual_names[i] = candidate_name
        available_lounge_names.remove(candidate_name)
        print(f"Matched: {name} → {candidate_name} ({score})")

    # Check aliases and override if higher confidence
    for i, name in enumerate(players):
        attempt: tuple[str, int] | None = process.extractOne(
            name, list((data_manager.Aliases.get_all_aliases()).values())
        )
        if attempt:
            potential_alias_match, certainty = attempt
            if potential_alias_match and certainty > 70:
                # Find the key for this alias value
                for alias_key, alias_val in (
                    data_manager.Aliases.get_all_aliases()
                ).items():
                    if alias_val == potential_alias_match:
                        actual_names[i] = alias_key
                        print(f"Alias match: {name} → {alias_key} ({certainty})")
                        break

    return actual_names
