import json
from pathlib import Path

_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "available-sites.json"


def get_available_sites():
    with open(_DATA_FILE, "r") as f:
        return json.load(f)


availableSites = get_available_sites()
