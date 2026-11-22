SELECT
  order_id_src,
  product_id_src,
  COALESCE(quantity, 0)                            AS quantity,
  COALESCE(price, 0)                               AS price,
  COALESCE(line_total, 0)                          AS line_total,
  COALESCE(discounted_line_total, line_total, 0)   AS discounted_line_total
FROM {{ source('raw', 'order_items') }}
