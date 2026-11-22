import time
from typing import Any, Dict, Iterator

import requests


def paged_get(url: str, items_key: str, limit: int = 100, pause: float = 0.2) -> Iterator[Dict[str, Any]]:
    """Yield every record from a DummyJSON-style paginated endpoint.

    DummyJSON responses look like {"<items_key>": [...], "total": N, "skip": S, "limit": L}.
    """
    skip = 0
    while True:
        resp = requests.get(url, params={"limit": limit, "skip": skip}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if items_key not in data:
            raise ValueError(f"Unexpected response from {url}: no '{items_key}' key")

        items = data[items_key]
        yield from items

        skip += len(items)
        if not items or skip >= data.get("total", 0):
            break
        time.sleep(pause)
