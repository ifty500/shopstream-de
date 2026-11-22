"""Provision Metabase for the demo: admin user, Postgres connection, dashboard.

Idempotent: re-running reuses the existing user/database and rebuilds the
dashboard. Run inside the app container:  make dashboard
"""
from __future__ import annotations

import os
import sys
import time

import requests

MB = os.getenv("MB_URL", "http://metabase:3000")
EMAIL = os.getenv("MB_ADMIN_EMAIL", "admin@shopstream.local")
PASSWORD = os.getenv("MB_ADMIN_PASSWORD", "ShopStream-dev-1")
DB_NAME = "ShopStream"
DASHBOARD_NAME = "ShopStream Sales Overview"

# (name, display, sql, visualization_settings, (col, row, size_x, size_y))
# Metabase dashboards use a 24-column grid.
CARDS = [
    ("Revenue (after discounts)", "scalar",
     "SELECT ROUND(SUM(discounted_total), 2) AS revenue FROM mart.fact_orders",
     {"column_settings": {'["name","revenue"]': {"prefix": "$"}}}, (0, 0, 6, 3)),
    ("Orders", "scalar",
     "SELECT COUNT(*) AS orders FROM mart.fact_orders",
     {}, (6, 0, 6, 3)),
    ("Average order value", "scalar",
     "SELECT ROUND(AVG(discounted_total), 2) AS aov FROM mart.fact_orders",
     {"column_settings": {'["name","aov"]': {"prefix": "$", "decimals": 0}}}, (12, 0, 6, 3)),
    ("Units sold", "scalar",
     "SELECT SUM(item_count) AS units FROM mart.fact_orders",
     {}, (18, 0, 6, 3)),
    ("Monthly revenue (synthetic order dates)", "line",
     """SELECT DATE_TRUNC('month', d.date)::date AS month,
       ROUND(SUM(f.discounted_total), 2) AS revenue
FROM mart.fact_orders f
JOIN mart.dim_date d ON d.date_key = f.order_date_key
GROUP BY 1 ORDER BY 1""",
     {"graph.dimensions": ["month"], "graph.metrics": ["revenue"]}, (0, 3, 24, 6)),
    ("Revenue by category", "bar",
     """SELECT p.category, ROUND(SUM(i.discounted_line_total), 2) AS revenue
FROM mart.fact_order_items i
JOIN mart.dim_products p ON p.product_key = i.product_key
GROUP BY 1 ORDER BY 2 DESC""",
     {"graph.dimensions": ["category"], "graph.metrics": ["revenue"]}, (0, 9, 12, 8)),
    ("Top 10 products by revenue", "row",
     """SELECT p.title AS product, ROUND(SUM(i.discounted_line_total), 2) AS revenue
FROM mart.fact_order_items i
JOIN mart.dim_products p ON p.product_key = i.product_key
GROUP BY 1 ORDER BY 2 DESC LIMIT 10""",
     {"graph.dimensions": ["product"], "graph.metrics": ["revenue"]}, (12, 9, 12, 8)),
    ("Top 10 cities by revenue", "bar",
     """SELECT u.city, ROUND(SUM(f.discounted_total), 2) AS revenue
FROM mart.fact_orders f
JOIN mart.dim_users u ON u.user_key = f.user_key
GROUP BY 1 ORDER BY 2 DESC LIMIT 10""",
     {"graph.dimensions": ["city"], "graph.metrics": ["revenue"]}, (0, 17, 12, 7)),
    ("Revenue by customer gender", "pie",
     """SELECT u.gender, ROUND(SUM(f.discounted_total), 2) AS revenue
FROM mart.fact_orders f
JOIN mart.dim_users u ON u.user_key = f.user_key
GROUP BY 1""",
     {"pie.dimension": "gender", "pie.metric": "revenue"}, (12, 17, 12, 7)),
]


def wait_for_metabase(timeout: int = 300) -> None:
    print(f"Waiting for Metabase at {MB} ...", flush=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if requests.get(f"{MB}/api/health", timeout=5).json().get("status") == "ok":
                return
        except (requests.RequestException, ValueError):
            pass
        time.sleep(3)
    sys.exit("Metabase did not become healthy in time")


def login() -> requests.Session:
    s = requests.Session()
    props = s.get(f"{MB}/api/session/properties").json()
    if not props.get("has-user-setup"):
        print("Creating Metabase admin user")
        r = s.post(f"{MB}/api/setup", json={
            "token": props["setup-token"],
            "user": {"email": EMAIL, "password": PASSWORD,
                     "first_name": "ShopStream", "last_name": "Admin",
                     "site_name": "ShopStream"},
            "prefs": {"site_name": "ShopStream", "allow_tracking": False},
        })
        r.raise_for_status()
        session_id = r.json()["id"]
    else:
        r = s.post(f"{MB}/api/session", json={"username": EMAIL, "password": PASSWORD})
        if r.status_code != 200:
            sys.exit("Metabase already set up with a different admin. "
                     "Set MB_ADMIN_EMAIL / MB_ADMIN_PASSWORD in .env to match.")
        session_id = r.json()["id"]
    s.headers["X-Metabase-Session"] = session_id
    return s


def ensure_database(s: requests.Session) -> int:
    dbs = s.get(f"{MB}/api/database").json()
    dbs = dbs.get("data", dbs) if isinstance(dbs, dict) else dbs
    for db in dbs:
        if db["name"] == DB_NAME:
            return db["id"]
    print("Connecting Metabase to Postgres")
    r = s.post(f"{MB}/api/database", json={
        "engine": "postgres",
        "name": DB_NAME,
        "details": {
            "host": os.getenv("POSTGRES_HOST", "postgres"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "dbname": os.environ["POSTGRES_DB"],
            "user": os.environ["POSTGRES_USER"],
            "password": os.environ["POSTGRES_PASSWORD"],
            "ssl": False,
            "schema-filters-type": "inclusion",
            "schema-filters-patterns": "mart",
        },
    })
    r.raise_for_status()
    return r.json()["id"]


def rebuild_dashboard(s: requests.Session, db_id: int) -> int:
    # Remove the previous version so re-runs don't pile up duplicates.
    for d in s.get(f"{MB}/api/dashboard").json():
        if d["name"] == DASHBOARD_NAME:
            dash = s.get(f"{MB}/api/dashboard/{d['id']}").json()
            for dc in dash.get("dashcards", []):
                if dc.get("card_id"):
                    s.delete(f"{MB}/api/card/{dc['card_id']}")
            s.delete(f"{MB}/api/dashboard/{d['id']}")

    dash_id = s.post(f"{MB}/api/dashboard", json={
        "name": DASHBOARD_NAME,
        "description": "Built automatically from the dbt mart schema by scripts/metabase_setup.py",
    }).json()["id"]

    dashcards = []
    for i, (name, display, sql, viz, (col, row, sx, sy)) in enumerate(CARDS):
        r = s.post(f"{MB}/api/card", json={
            "name": name,
            "display": display,
            "visualization_settings": viz,
            "dataset_query": {"type": "native", "native": {"query": sql}, "database": db_id},
        })
        r.raise_for_status()
        dashcards.append({"id": -(i + 1), "card_id": r.json()["id"],
                          "col": col, "row": row, "size_x": sx, "size_y": sy,
                          "parameter_mappings": [], "visualization_settings": {}})

    s.put(f"{MB}/api/dashboard/{dash_id}", json={"dashcards": dashcards}).raise_for_status()
    return dash_id


def main() -> None:
    wait_for_metabase()
    s = login()
    db_id = ensure_database(s)
    dash_id = rebuild_dashboard(s, db_id)
    print("\nDashboard ready: http://localhost:3000/dashboard/%d" % dash_id)
    print(f"Log in with {EMAIL} / the MB_ADMIN_PASSWORD from .env")


if __name__ == "__main__":
    main()
