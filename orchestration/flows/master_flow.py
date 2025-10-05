from prefect import flow
from .extract_users import extract_users
from .extract_products import extract_products
from .extract_orders import extract_orders
from .load_raw import load_users, load_products, load_orders
from .great_expectations_check import ge_check
from .run_dbt import run_dbt_all

@flow(name="shopstream-master")
def master_flow():
    users = extract_users()
    load_users(users)
    ge_check("raw_users")

    products = extract_products()
    load_products(products)
    ge_check("raw_products")

    orders = extract_orders()
    load_orders(orders)
    ge_check("raw_orders")

    run_dbt_all()

if __name__ == "__main__":
    master_flow()
