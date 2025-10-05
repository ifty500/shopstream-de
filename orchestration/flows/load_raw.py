from prefect import task
from pipelines.load.postgres_loader import upsert_users, upsert_products, upsert_orders_and_items

@task
def load_users(rows):
    upsert_users(rows)

@task
def load_products(rows):
    upsert_products(rows)

@task
def load_orders(rows):
    upsert_orders_and_items(rows)
