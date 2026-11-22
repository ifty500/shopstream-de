SELECT
  CONCAT(oi.order_id_src, '-', oi.product_id_src) AS order_item_key,
  oi.order_id_src                                 AS order_key,
  oi.product_id_src                               AS product_key,
  o.user_id_src                                   AS user_key,
  TO_CHAR(o.order_date, 'YYYYMMDD')::int          AS order_date_key,
  oi.quantity,
  oi.price,
  oi.line_total,
  oi.discounted_line_total
FROM {{ ref('stg_order_items') }} oi
JOIN {{ ref('stg_orders') }} o ON o.id_src = oi.order_id_src
