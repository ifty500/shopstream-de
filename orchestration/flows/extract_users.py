from prefect import task
from pipelines.extract.dummyjson import iter_users

@task(retries=3, retry_delay_seconds=5)
def extract_users():
    return list(iter_users())
