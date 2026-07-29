import json
import os
from urllib.parse import quote

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))          # .../sites
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)                       # project root
_CONFIG_PATH = os.path.join(_PROJECT_ROOT, "data", "available-sites.json")

with open(_CONFIG_PATH, encoding="utf-8") as _f:
    SITES = json.load(_f)


def get_base_url(site_key: str) -> str:
    return SITES[site_key]["base_url"]


def available_sites() -> list:
    """Return the list of supported site keys, e.g. ['amazon_tr', 'hepsiburada']."""
    return list(SITES.keys())

if __name__ == "__main__":
    print(available_sites())