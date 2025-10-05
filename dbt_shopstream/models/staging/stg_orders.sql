{{ config(unique_key='id_src') }}
SELECT
  id_src,
  user_id_src,
  COALESCE(total_amount, 0) AS total_amount,
  COALESCE(item_count, 0)   AS item_count,
  COALESCE(order_date, CURRENT_DATE) AS order_date,
  ingested_at
FROM raw_orders
