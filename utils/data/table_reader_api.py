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
        candidate_name, score, _ = match_result
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
        candidate_name, score, _ = match_result
        actual_names[i] = candidate_name
        available_lounge_names.remove(candidate_name)
        print(f"Matched: {name} → {candidate_name} ({score})")

    # Check aliases and override if higher confidence
    all_aliases = await data_manager.Aliases.get_all_aliases()

    for i, name in enumerate(players):
        attempt: tuple[str, int] | None = process.extractOne(
            name, list(all_aliases.values())
        )
        if attempt:
            potential_alias_match, certainty, _ = attempt
            if potential_alias_match and certainty > 70:
                # Find the key for this alias value
                for alias_key, alias_val in all_aliases.items():
                    if alias_val == potential_alias_match:
                        # Only override if the alias key is in lounge_names and not already used
                        if alias_key in lounge_names and alias_key not in actual_names:
                            # Return the old name to the pool
                            if actual_names[i]:
                                available_lounge_names.append(actual_names[i])
                            actual_names[i] = alias_key
                            print(f"Alias match: {name} → {alias_key} ({certainty})")
                        break

    # Pass 3: Final validation and cleanup - ensure no duplicates and all names assigned
    used_names = set()
    for i, assigned_name in enumerate(actual_names):
        if assigned_name in used_names:
            # Duplicate detected - reassign from available pool
            print(f"Duplicate detected: {assigned_name} at position {i}")
            if available_lounge_names:
                new_name = available_lounge_names.pop(0)
                actual_names[i] = new_name
                print(f"Reassigned to: {new_name}")
            else:
                print(f"No available names left for position {i}")
                return None
        else:
            used_names.add(assigned_name)

    # Verify all names are assigned
    if None in actual_names:
        print("Error: Some names were not assigned")
        return None

    # Verify correct count
    if len(set(actual_names)) != len(lounge_names):
        print(
            f"Error: Name count mismatch. Expected {len(lounge_names)}, got {len(set(actual_names))}"
        )
        return None

    print(f"Final assignments: {actual_names}")
    return actual_names
