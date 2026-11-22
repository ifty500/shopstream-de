-- DummyJSON carts carry no order date. When the source doesn't provide one,
-- derive a stable synthetic date from the order id (spread across 2024) so the
-- value doesn't change between runs and always falls inside dim_date.
SELECT
  id_src,
  user_id_src,
  COALESCE(total_amount, 0)                     AS total_amount,
  COALESCE(discounted_total, total_amount, 0)   AS discounted_total,
  COALESCE(product_count, 0)                    AS product_count,
  COALESCE(item_count, 0)                       AS item_count,
  COALESCE(order_date, DATE '2024-01-01' + ((id_src * 37) % 366)::int) AS order_date,
  (order_date IS NULL)                          AS order_date_is_synthetic,
  ingested_at
FROM {{ source('raw', 'orders') }}
