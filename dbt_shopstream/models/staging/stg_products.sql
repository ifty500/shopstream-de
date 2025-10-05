{{ config(unique_key='id_src') }}
WITH latest AS (
    SELECT
        id_src, title, category, price, brand, ingested_at,
        ROW_NUMBER() OVER (PARTITION BY id_src ORDER BY ingested_at DESC) AS rn
    FROM raw_products
)
SELECT id_src, title, category, price, brand, ingested_at
FROM latest
WHERE rn = 1
