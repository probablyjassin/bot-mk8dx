import aiohttp
from io import BufferedReader
from typing import TypedDict, cast
from rapidfuzz import process

from utils.data import data_manager
from config import TABLE_READER_URL


class OCRPlayerList(TypedDict):
    position: int
    name: str
    score: str


async def table_read_ocr_api(file: BufferedReader) -> list[OCRPlayerList]:
    """
    Send a buffered binary file to the table reader API and return the JSON response.
    """
    try:
        file.seek(0)
    except Exception:
        pass

    file_content = file.read()

    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field(
            "file",
            file_content,
            filename="test_img.png",
            content_type="image/png",
        )

        async with session.post(
            TABLE_READER_URL,
            data=data,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            response.raise_for_status()
            result = await response.json()

            if not result["players"]:
                return None

            return cast(list[OCRPlayerList], result["players"])


def ocr_to_tablestring(ocr_names: list[str], scores: list[str]) -> str:
    tablestring = "-\n"
    for i, name in enumerate(ocr_names):
        tablestring += f"{name} {scores[i]}+\n\n"
    return tablestring


async def pattern_match_lounge_names(
    players: list[str], lounge_names: list[str]
) -> list[str] | None:
    """
    Match OCR-detected player names to their actual lounge names using fuzzy matching.
    Uses a multi-pass approach with alias checking for better accuracy.
    """
    if len(players) != len(lounge_names):
        print(
            f"Error: Player count mismatch. OCR: {len(players)}, Lounge: {len(lounge_names)}"
        )
        return None

    print("--- Pattern matching results ---")

    # Fetch aliases once upfront
    all_aliases = await data_manager.Aliases.get_all_aliases()

    # Create a scoring map for all possible matches
    match_scores = {}
    for ocr_name in players:
        match_scores[ocr_name] = {}

        # Score against lounge names
        for lounge_name in lounge_names:
            result = process.extractOne(ocr_name, [lounge_name])
            if result:
                match_scores[ocr_name][lounge_name] = result[1]

        # Score against aliases (map back to actual lounge name)
        for alias_key, alias_val in all_aliases.items():
            if alias_key in lounge_names:
                result = process.extractOne(ocr_name, [alias_val])
                if result:
                    # Use alias score if it's better than direct match
                    current_score = match_scores[ocr_name].get(alias_key, 0)
                    match_scores[ocr_name][alias_key] = max(current_score, result[1])

    # Greedy matching: assign best matches first
    assigned = {}
    used_lounge_names = set()

    # Sort OCR names by their best match score (descending)
    sorted_players = sorted(
        players,
        key=lambda p: max(match_scores[p].values()) if match_scores[p] else 0,
        reverse=True,
    )

    for ocr_name in sorted_players:
        # Find best available match
        best_match = None
        best_score = 0

        for lounge_name, score in match_scores[ocr_name].items():
            if lounge_name not in used_lounge_names and score > best_score:
                best_match = lounge_name
                best_score = score

        if best_match is None:
            print(f"Failed to match: {ocr_name}")
            return None

        assigned[ocr_name] = best_match
        used_lounge_names.add(best_match)

        # Check if match was via alias
        alias_used = ""
        for alias_key, alias_val in all_aliases.items():
            if alias_key == best_match:
                result = process.extractOne(ocr_name, [alias_val])
                if result and result[1] >= best_score:
                    alias_used = f" (via alias '{alias_val}')"
                    break

        confidence = (
            "HIGH" if best_score > 90 else "MEDIUM" if best_score > 70 else "LOW"
        )
        print(f"[{confidence}] {ocr_name} → {best_match} ({best_score}){alias_used}")

    # Reconstruct in original player order
    result = [assigned[name] for name in players]

    # Validation
    if len(set(result)) != len(lounge_names):
        print(f"Error: Duplicate assignments detected")
        return None

    print(f"✓ Successfully matched all {len(players)} players")
    return result
