SELECT
  o.id_src                                AS order_key,
  o.id_src                                AS order_id_src,
  o.user_id_src                           AS user_key,
  TO_CHAR(o.order_date, 'YYYYMMDD')::int  AS order_date_key,
  o.total_amount,
  o.discounted_total,
  o.total_amount - o.discounted_total     AS discount_amount,
  o.product_count,
  o.item_count,
  o.order_date_is_synthetic
FROM {{ ref('stg_orders') }} o
