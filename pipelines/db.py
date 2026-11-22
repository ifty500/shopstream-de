"""Shared database connection for the pipeline."""
from __future__ import annotations

import os
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL


def pg_url() -> URL:
    """Build the Postgres URL from POSTGRES_* env vars.

    URL.create escapes special characters, so passwords containing
    '@', ':' or '/' work.
    """
    return URL.create(
        drivername="postgresql+psycopg2",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.environ["POSTGRES_DB"],
    )


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(pg_url(), pool_pre_ping=True)
