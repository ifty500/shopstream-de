import json

from pipelines.load.postgres_loader import map_order, map_order_items, map_product, map_user


def test_map_user_builds_full_name_and_city():
    row = map_user({"id": 1, "firstName": "Emily", "lastName": "Johnson",
                    "email": "e@x.com", "gender": "female",
                    "address": {"city": "Phoenix"}})
    assert row["id_src"] == 1
    assert row["name"] == "Emily Johnson"
    assert row["city"] == "Phoenix"
    assert json.loads(row["payload"])["email"] == "e@x.com"


def test_map_user_handles_missing_fields():
    row = map_user({"id": 2})
    assert row["name"] is None
    assert row["city"] is None


def test_map_product_includes_brand():
    row = map_product({"id": 5, "title": "Mascara", "category": "beauty",
                       "price": 9.99, "brand": "Essence"})
    assert row["brand"] == "Essence"
    assert row["price"] == 9.99


CART = {
    "id": 10, "userId": 33, "total": 150.0, "discountedTotal": 135.0,
    "totalProducts": 2, "totalQuantity": 5,
    "products": [
        {"id": 1, "price": 10.0, "quantity": 3, "total": 30.0, "discountedTotal": 27.0},
        {"id": 2, "price": 60.0, "quantity": 2, "total": 120.0, "discountedTotal": 108.0},
    ],
}


def test_map_order_separates_product_and_unit_counts():
    row = map_order(CART)
    assert row["product_count"] == 2
    assert row["item_count"] == 5
    assert row["discounted_total"] == 135.0
    assert row["order_date"] is None  # DummyJSON carts have no date


def test_map_order_items():
    items = map_order_items(CART)
    assert [(i["order_id_src"], i["product_id_src"]) for i in items] == [(10, 1), (10, 2)]
    assert items[1]["discounted_line_total"] == 108.0


def test_map_order_items_empty_cart():
    assert map_order_items({"id": 11, "products": None}) == []


def test_map_order_items_merges_duplicate_product_lines():
    # Real DummyJSON quirk (e.g. cart 69): same product on two lines.
    cart = {"id": 69, "products": [
        {"id": 122, "price": 299.99, "quantity": 2, "total": 599.98, "discountedTotal": 560.0},
        {"id": 122, "price": 299.99, "quantity": 5, "total": 1499.95, "discountedTotal": 1400.0},
        {"id": 7, "price": 10.0, "quantity": 1, "total": 10.0, "discountedTotal": 9.0},
    ]}
    items = {i["product_id_src"]: i for i in map_order_items(cart)}
    assert len(items) == 2
    assert items[122]["quantity"] == 7
    assert items[122]["line_total"] == 2099.93
    assert items[122]["discounted_line_total"] == 1960.0
