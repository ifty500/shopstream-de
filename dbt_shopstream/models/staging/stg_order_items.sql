{{ config(materialized='incremental') }}
SELECT
  oi.order_id_src,
  oi.product_id_src,
  COALESCE(oi.quantity, 0)     AS quantity,
  COALESCE(oi.price, 0.0)      AS price,
  COALESCE(oi.line_total, 0.0) AS line_total
FROM raw_order_items oi
