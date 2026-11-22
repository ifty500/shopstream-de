"""Load extracted DummyJSON records into the raw schema.

Each source record is mapped to a row by a pure function (easy to unit test),
then written in a single transaction with batched executemany upserts.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List

from sqlalchemy import text

from pipelines.db import get_engine

Row = Dict[str, Any]


# ---------- mapping: source record -> raw row ----------

def map_user(u: Row) -> Row:
    full_name = " ".join(filter(None, [u.get("firstName"), u.get("lastName")]))
    return {
        "id_src": u.get("id"),
        "name": full_name or None,
        "email": u.get("email"),
        "gender": u.get("gender"),
        "city": (u.get("address") or {}).get("city"),
        "payload": json.dumps(u),
    }


def map_product(p: Row) -> Row:
    return {
        "id_src": p.get("id"),
        "title": p.get("title"),
        "category": p.get("category"),
        "price": p.get("price"),
        "brand": p.get("brand"),
        "description": p.get("description"),
        "payload": json.dumps(p),
    }


def map_order(c: Row) -> Row:
    return {
        "id_src": c.get("id"),
        "user_id_src": c.get("userId"),
        "total_amount": c.get("total"),
        "discounted_total": c.get("discountedTotal"),
        "product_count": c.get("totalProducts"),
        "item_count": c.get("totalQuantity"),
        "order_date": c.get("date"),  # DummyJSON carts have no date; stays NULL
        "payload": json.dumps(c),
    }


def map_order_items(c: Row) -> List[Row]:
    """One row per (order, product).

    Some DummyJSON carts list the same product on two lines, and the cart total
    counts both. Merge them (summing quantity and totals) instead of letting
    one line overwrite the other, so item revenue still adds up to the order.
    """
    merged: Dict[Any, Row] = {}
    for it in c.get("products") or []:
        pid = it.get("id")
        if pid not in merged:
            merged[pid] = {
                "order_id_src": c.get("id"),
                "product_id_src": pid,
                "quantity": 0,
                "price": it.get("price"),
                "line_total": 0.0,
                "discounted_line_total": 0.0,
            }
        row = merged[pid]
        row["quantity"] += it.get("quantity") or 0
        row["line_total"] = round(row["line_total"] + (it.get("total") or 0), 2)
        row["discounted_line_total"] = round(
            row["discounted_line_total"] + (it.get("discountedTotal") or it.get("total") or 0), 2)
    return list(merged.values())


# ---------- SQL ----------

USERS_UPSERT = text("""
    INSERT INTO raw.users (id_src, name, email, gender, city, payload, ingested_at)
    VALUES (:id_src, :name, :email, :gender, :city, CAST(:payload AS JSONB), now())
    ON CONFLICT (id_src) DO UPDATE SET
      name = EXCLUDED.name, email = EXCLUDED.email, gender = EXCLUDED.gender,
      city = EXCLUDED.city, payload = EXCLUDED.payload, ingested_at = now()
""")

PRODUCTS_UPSERT = text("""
    INSERT INTO raw.products (id_src, title, category, price, brand, description, payload, ingested_at)
    VALUES (:id_src, :title, :category, :price, :brand, :description, CAST(:payload AS JSONB), now())
    ON CONFLICT (id_src) DO UPDATE SET
      title = EXCLUDED.title, category = EXCLUDED.category, price = EXCLUDED.price,
      brand = EXCLUDED.brand, description = EXCLUDED.description,
      payload = EXCLUDED.payload, ingested_at = now()
""")

ORDERS_UPSERT = text("""
    INSERT INTO raw.orders (id_src, user_id_src, total_amount, discounted_total,
                            product_count, item_count, order_date, payload, ingested_at)
    VALUES (:id_src, :user_id_src, :total_amount, :discounted_total,
            :product_count, :item_count, :order_date, CAST(:payload AS JSONB), now())
    ON CONFLICT (id_src) DO UPDATE SET
      user_id_src = EXCLUDED.user_id_src, total_amount = EXCLUDED.total_amount,
      discounted_total = EXCLUDED.discounted_total, product_count = EXCLUDED.product_count,
      item_count = EXCLUDED.item_count, order_date = EXCLUDED.order_date,
      payload = EXCLUDED.payload, ingested_at = now()
""")

# Items are replaced per order, so products removed from a cart disappear too.
ITEMS_DELETE = text("DELETE FROM raw.order_items WHERE order_id_src = ANY(:order_ids)")

ITEMS_INSERT = text("""
    INSERT INTO raw.order_items (order_id_src, product_id_src, quantity, price,
                                 line_total, discounted_line_total, ingested_at)
    VALUES (:order_id_src, :product_id_src, :quantity, :price,
            :line_total, :discounted_line_total, now())
    ON CONFLICT (order_id_src, product_id_src) DO UPDATE SET
      quantity = EXCLUDED.quantity, price = EXCLUDED.price, line_total = EXCLUDED.line_total,
      discounted_line_total = EXCLUDED.discounted_line_total, ingested_at = now()
""")


# ---------- loaders ----------

def upsert_users(records: Iterable[Row]) -> int:
    rows = [map_user(u) for u in records]
    if rows:
        with get_engine().begin() as cx:
            cx.execute(USERS_UPSERT, rows)
    return len(rows)


def upsert_products(records: Iterable[Row]) -> int:
    rows = [map_product(p) for p in records]
    if rows:
        with get_engine().begin() as cx:
            cx.execute(PRODUCTS_UPSERT, rows)
    return len(rows)


def upsert_orders_and_items(records: Iterable[Row]) -> int:
    carts = list(records)
    orders = [map_order(c) for c in carts]
    items = [it for c in carts for it in map_order_items(c)]
    if orders:
        with get_engine().begin() as cx:
            cx.execute(ORDERS_UPSERT, orders)
            cx.execute(ITEMS_DELETE, {"order_ids": [o["id_src"] for o in orders]})
            if items:
                cx.execute(ITEMS_INSERT, items)
    return len(orders)
