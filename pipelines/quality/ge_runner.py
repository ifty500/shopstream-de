"""Data quality checks with Great Expectations.

`validate_*` functions run on the extracted records *before* they are loaded,
so bad data never reaches the warehouse. `check_loaded_count` runs afterwards
to confirm the load landed.
"""
from __future__ import annotations

from typing import Any, Dict, List, Sequence

import great_expectations as ge
import pandas as pd
from sqlalchemy import text

from pipelines.db import get_engine
from pipelines.load.postgres_loader import map_order_items


class DataQualityError(AssertionError):
    pass


def _run(name: str, df: pd.DataFrame, checks: List[tuple]) -> None:
    ds = ge.from_pandas(df)
    failures = []
    for expectation, kwargs in checks:
        result = getattr(ds, expectation)(**kwargs)
        if not result.success:
            failures.append(f"{expectation}({kwargs})")
    if failures:
        raise DataQualityError(f"[{name}] failed checks: " + "; ".join(failures))


def _entity_checks(id_col: str, not_null: Sequence[str] = ()) -> List[tuple]:
    checks = [
        ("expect_table_row_count_to_be_between", {"min_value": 1}),
        ("expect_column_values_to_not_be_null", {"column": id_col}),
        ("expect_column_values_to_be_unique", {"column": id_col}),
    ]
    checks += [("expect_column_values_to_not_be_null", {"column": c}) for c in not_null]
    return checks


def validate_users(records: List[Dict[str, Any]]) -> None:
    _run("users", pd.DataFrame(records), _entity_checks("id", ["email"]))


def validate_products(records: List[Dict[str, Any]]) -> None:
    df = pd.DataFrame(records)
    checks = _entity_checks("id", ["title", "category", "price"])
    checks.append(("expect_column_values_to_be_between", {"column": "price", "min_value": 0}))
    _run("products", df, checks)


def validate_orders(records: List[Dict[str, Any]]) -> None:
    orders = pd.DataFrame(records)
    checks = _entity_checks("id", ["userId", "total"])
    checks.append(("expect_column_values_to_be_between", {"column": "total", "min_value": 0}))
    _run("orders", orders, checks)

    items = pd.DataFrame([it for c in records for it in map_order_items(c)])
    _run("order_items", items, [
        ("expect_table_row_count_to_be_between", {"min_value": 1}),
        ("expect_compound_columns_to_be_unique", {"column_list": ["order_id_src", "product_id_src"]}),
        ("expect_column_values_to_not_be_null", {"column": "product_id_src"}),
        ("expect_column_values_to_be_between", {"column": "quantity", "min_value": 1}),
    ])


def check_loaded_count(table: str, expected_min: int) -> int:
    """Confirm the raw table holds at least as many rows as we just loaded."""
    allowed = {"raw.users", "raw.products", "raw.orders", "raw.order_items"}
    if table not in allowed:
        raise ValueError(f"Unknown table {table}")
    with get_engine().connect() as cx:
        n = cx.execute(text(f"SELECT count(*) FROM {table}")).scalar_one()
    if n < expected_min:
        raise DataQualityError(f"{table} has {n} rows, expected at least {expected_min}")
    return n
