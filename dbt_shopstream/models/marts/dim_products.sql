SELECT
  id_src AS product_key,
  id_src AS product_id_src,
  title, category, price, brand
FROM {{ ref('stg_products') }}
