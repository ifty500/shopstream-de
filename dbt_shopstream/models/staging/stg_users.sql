SELECT
  id_src,
  name,
  LOWER(email) AS email,
  gender,
  city,
  ingested_at
FROM {{ source('raw', 'users') }}
