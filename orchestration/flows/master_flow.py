from prefect import flow

from .tasks import (extract_orders, extract_products, extract_users, load,
                    run_dbt_build, validate)


@flow(name="shopstream-master")
def master_flow():
    # Extract all three sources concurrently.
    users_f = extract_users.submit()
    products_f = extract_products.submit()
    orders_f = extract_orders.submit()

    # Validate before loading: if any source fails its checks, nothing is
    # loaded and dbt doesn't run.
    sources = {"users": users_f.result(),
               "products": products_f.result(),
               "orders": orders_f.result()}
    for entity, records in sources.items():
        validate(entity, records)

    for entity, records in sources.items():
        load(entity, records)

    run_dbt_build()


if __name__ == "__main__":
    master_flow()
