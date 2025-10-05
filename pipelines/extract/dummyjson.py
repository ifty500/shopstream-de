from .common import paged_get

BASE = "https://dummyjson.com"

def iter_users():
    yield from paged_get(f"{BASE}/users")

def iter_products():
    yield from paged_get(f"{BASE}/products")

def iter_carts():
    yield from paged_get(f"{BASE}/carts")
