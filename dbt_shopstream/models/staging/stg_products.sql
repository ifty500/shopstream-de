SELECT
  id_src,
  title,
  category,
  price,
  COALESCE(brand, 'Unknown') AS brand,
  ingested_at
FROM {{ source('raw', 'products') }}
