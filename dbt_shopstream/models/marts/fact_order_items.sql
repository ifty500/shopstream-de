SELECT
  CONCAT(oi.order_id_src, '-', oi.product_id_src) AS order_item_key,
  oi.order_id_src,
  oi.product_id_src,
  oi.quantity,
  oi.price,
  oi.line_total
FROM {{ ref('stg_order_items') }} oi
