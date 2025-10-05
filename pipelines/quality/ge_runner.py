# pipelines/quality/ge_runner.py
from __future__ import annotations

import os
import pandas as pd
import great_expectations as ge
from sqlalchemy import create_engine


def pg_url() -> str:
    return (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    )


def _load_table_as_ge_dataset(table: str) -> ge.dataset.PandasDataset:
    """
    Load a Postgres table into a pandas DataFrame, then wrap it as a GE PandasDataset.
    Works with GE 0.18.x where `from_pandas_sql` no longer exists.
    """
    eng = create_engine(pg_url(), future=True)
    with eng.connect() as cx:
        df = pd.read_sql_query(f'SELECT * FROM "{table}"', cx)  # quote to be safe
    return ge.from_pandas(df)


def check_table_not_empty(table: str) -> None:
    ds = _load_table_as_ge_dataset(table)
    # At least 1 row expected
    res = ds.expect_table_row_count_to_be_between(min_value=1)
    if not res.success:
        raise AssertionError(f"GE check failed: '{table}' is empty")


def check_id_src_not_null_and_unique(table: str, id_col: str = "id_src") -> None:
    ds = _load_table_as_ge_dataset(table)

    res1 = ds.expect_column_values_to_not_be_null(id_col)
    if not res1.success:
        raise AssertionError(f"GE check failed: '{table}.{id_col}' contains NULLs")

    res2 = ds.expect_column_values_to_be_unique(id_col)
    if not res2.success:
        raise AssertionError(f"GE check failed: '{table}.{id_col}' contains duplicates")
