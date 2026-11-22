WITH dates AS (
  SELECT d::date AS date
  FROM generate_series(date '2022-01-01', CURRENT_DATE, interval '1 day') AS t(d)
)
SELECT
  TO_CHAR(date, 'YYYYMMDD')::int AS date_key,
  date,
  EXTRACT(YEAR FROM date)::int    AS year,
  EXTRACT(QUARTER FROM date)::int AS quarter,
  EXTRACT(MONTH FROM date)::int   AS month,
  TO_CHAR(date, 'Mon')            AS month_name,
  EXTRACT(DAY FROM date)::int     AS day,
  EXTRACT(ISODOW FROM date)::int  AS weekday,       -- 1 = Monday
  EXTRACT(ISODOW FROM date) >= 6  AS is_weekend
FROM dates
