from pathlib import Path
from typing import Any

import orjson


parent_folder = Path(__file__).parent
test_gamedata = parent_folder / "test_data_gamedata"


def get_response_data(folder: str, file_name: str) -> Any:
    """Return test data given folder and file name"""
    with open(parent_folder / folder / f"{file_name}.json", "rb") as fp:
        return orjson.loads(fp.read())


def get_text_data(folder: str, file_name: str) -> str:
    """Return test data given folder and file name"""
    with open(parent_folder / folder / f"{file_name}.txt", "r", encoding="utf-8") as fp:
        return fp.read()
