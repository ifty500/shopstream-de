import time
import requests
from typing import Iterator, Dict, Any

def paged_get(url: str, page_param: str = "skip", limit: int = 100) -> Iterator[Dict[str, Any]]:
    skip = 0
    while True:
        resp = requests.get(url, params={"limit": limit, page_param: skip}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        items_key = None
        for k in ("users","products","carts"):
            if k in data:
                items_key = k
                break
        if items_key is None:
            break
        items = data[items_key]
        if not items:
            break
        for it in items:
            yield it
        skip += limit
        time.sleep(0.2)
