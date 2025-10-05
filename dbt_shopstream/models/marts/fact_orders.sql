WITH o AS (SELECT * FROM {{ ref('stg_orders') }})
SELECT
  o.id_src AS order_key,
  o.id_src AS order_id_src,
  o.user_id_src,
  TO_CHAR(o.order_date, 'YYYYMMDD')::int AS order_date_key,
  o.total_amount,
  o.item_count
FROM o
