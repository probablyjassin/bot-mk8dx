import requests
from io import BufferedReader
from config import TABLE_READER_URL
from typing import TypedDict, List, Literal, cast


class Player(TypedDict):
    position: int
    name: str
    score: str


class TableReadResult(TypedDict):
    success: bool
    table_detected: bool
    team_mode: Literal["FFA"]
    player_count: int
    players: List[Player]


def table_read_ocr_api(file: BufferedReader) -> TableReadResult:
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

    return cast(TableReadResult, response.json())
