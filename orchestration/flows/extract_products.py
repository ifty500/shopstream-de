from prefect import task
from pipelines.extract.dummyjson import iter_products

@task(retries=3, retry_delay_seconds=5)
def extract_products():
    return list(iter_products())
