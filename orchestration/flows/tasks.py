"""Prefect tasks wrapping the pipeline steps."""
import subprocess

from prefect import get_run_logger, task

from pipelines.extract import dummyjson
from pipelines.load import postgres_loader as loader
from pipelines.quality import ge_runner as dq


# ----- extract (network calls, so retried) -----

@task(retries=3, retry_delay_seconds=5)
def extract_users():
    return list(dummyjson.iter_users())


@task(retries=3, retry_delay_seconds=5)
def extract_products():
    return list(dummyjson.iter_products())


@task(retries=3, retry_delay_seconds=5)
def extract_orders():
    return list(dummyjson.iter_carts())


# ----- validate before loading -----

@task
def validate(entity: str, records):
    {"users": dq.validate_users,
     "products": dq.validate_products,
     "orders": dq.validate_orders}[entity](records)
    get_run_logger().info("%s: %d records passed quality checks", entity, len(records))


# ----- load + post-load check -----

@task
def load(entity: str, records) -> int:
    fn = {"users": loader.upsert_users,
          "products": loader.upsert_products,
          "orders": loader.upsert_orders_and_items}[entity]
    n = fn(records)
    total = dq.check_loaded_count(f"raw.{entity}", n)
    get_run_logger().info("%s: upserted %d rows (raw.%s now has %d)", entity, n, entity, total)
    return n


# ----- transform -----

@task
def run_dbt_build():
    """dbt build = run models and their tests in dependency order."""
    subprocess.run(["dbt", "build", "--profiles-dir", "."], cwd="dbt_shopstream", check=True)
