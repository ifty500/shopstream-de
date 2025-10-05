SELECT
  id_src AS user_key,
  id_src AS user_id_src,
  name, email, gender, city
FROM {{ ref('stg_users') }}
