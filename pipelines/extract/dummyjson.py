from .common import paged_get

BASE = "https://dummyjson.com"


def iter_users():
    yield from paged_get(f"{BASE}/users", "users")


def iter_products():
    yield from paged_get(f"{BASE}/products", "products")


def iter_carts():
    """DummyJSON carts are treated as orders."""
    yield from paged_get(f"{BASE}/carts", "carts")
