from prefect import task
import subprocess, os

@task
def run_dbt_all():
    env = os.environ.copy()
    cmd = "cd dbt_shopstream && dbt deps && dbt run && dbt test"
    subprocess.check_call(cmd, shell=True, env=env)
