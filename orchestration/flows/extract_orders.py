from prefect import task
from pipelines.extract.dummyjson import iter_carts

@task(retries=3, retry_delay_seconds=5)
def extract_orders():
    return list(iter_carts())
