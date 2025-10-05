from typing import Iterable, Dict, Any
from sqlalchemy import create_engine, text
import os
import json


def pg_url() -> str:
    """
    Build a SQLAlchemy connection URL from environment variables.
    These are set via .env and docker-compose:
      POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB
    """
    return (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    )


def upsert_users(rows: Iterable[Dict[str, Any]]) -> None:
    """
    Upsert users into raw_users.
    Note: use :named binds consistently and CAST(:payload AS JSONB) to avoid parser issues.
    """
    eng = create_engine(pg_url(), future=True)
    stmt = text("""
        INSERT INTO raw_users (id_src, name, email, gender, city, payload, ingested_at)
        VALUES (:id_src, :name, :email, :gender, :city, CAST(:payload AS JSONB), now())
        ON CONFLICT (id_src) DO UPDATE SET
          name=EXCLUDED.name,
          email=EXCLUDED.email,
          gender=EXCLUDED.gender,
          city=EXCLUDED.city,
          payload=EXCLUDED.payload,
          ingested_at=now()
    """)
    with eng.begin() as cx:
        for u in rows:
            full_name = " ".join(filter(None, [u.get("firstName"), u.get("lastName")]))
            cx.execute(stmt, {
                "id_src": u.get("id"),
                "name": full_name or None,
                "email": u.get("email"),
                "gender": u.get("gender"),
                "city": (u.get("address") or {}).get("city"),
                "payload": json.dumps(u),
            })


def upsert_products(rows: Iterable[Dict[str, Any]]) -> None:
    """
    Upsert products into raw_products.
    """
    eng = create_engine(pg_url(), future=True)
    stmt = text("""
        INSERT INTO raw_products (id_src, title, description, price, category, payload, ingested_at)
        VALUES (:id_src, :title, :description, :price, :category, CAST(:payload AS JSONB), now())
        ON CONFLICT (id_src) DO UPDATE SET
          title=EXCLUDED.title,
          description=EXCLUDED.description,
          price=EXCLUDED.price,
          category=EXCLUDED.category,
          payload=EXCLUDED.payload,
          ingested_at=now()
    """)
    with eng.begin() as cx:
        for p in rows:
            cx.execute(stmt, {
                "id_src": p.get("id"),
                "title": p.get("title"),
                "description": p.get("description"),
                "price": p.get("price"),
                "category": p.get("category"),
                "payload": json.dumps(p),
            })


def upsert_orders_and_items(rows: Iterable[Dict[str, Any]]) -> None:
    """
    Upsert orders into raw_orders and items into raw_order_items.
    """
    eng = create_engine(pg_url(), future=True)

    order_stmt = text("""
        INSERT INTO raw_orders (id_src, user_id_src, total_amount, item_count, order_date, payload, ingested_at)
        VALUES (:id_src, :user_id_src, :total_amount, :item_count, :order_date, CAST(:payload AS JSONB), now())
        ON CONFLICT (id_src) DO UPDATE SET
          user_id_src=EXCLUDED.user_id_src,
          total_amount=EXCLUDED.total_amount,
          item_count=EXCLUDED.item_count,
          order_date=EXCLUDED.order_date,
          payload=EXCLUDED.payload,
          ingested_at=now()
    """)

    item_stmt = text("""
        INSERT INTO raw_order_items (order_id_src, product_id_src, quantity, price, line_total)
        VALUES (:order_id_src, :product_id_src, :quantity, :price, :line_total)
        ON CONFLICT (order_id_src, product_id_src) DO UPDATE SET
          quantity=EXCLUDED.quantity,
          price=EXCLUDED.price,
          line_total=EXCLUDED.line_total
    """)

    with eng.begin() as cx:
        for cart in rows:
            oid = cart.get("id")
            uid = cart.get("userId")
            total = cart.get("total")
            # DummyJSON has either totalProducts or totalQuantity depending on endpoint/version
            count = cart.get("totalProducts") or cart.get("totalQuantity")
            date = cart.get("date") or cart.get("updatedAt")  # best-effort fallback if provided

            cx.execute(order_stmt, {
                "id_src": oid,
                "user_id_src": uid,
                "total_amount": total,
                "item_count": count,
                "order_date": date,
                "payload": json.dumps(cart),
            })

            for it in cart.get("products", []):
                cx.execute(item_stmt, {
                    "order_id_src": oid,
                    "product_id_src": it.get("id"),
                    "quantity": it.get("quantity", 0),
                    "price": it.get("price", 0.0),
                    "line_total": it.get("total", 0.0),
                })
