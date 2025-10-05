from prefect import task
from pipelines.quality.ge_runner import check_table_not_empty

@task
def ge_check(table: str):
    check_table_not_empty(table)
