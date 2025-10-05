WITH dates AS (
  SELECT d::date AS date
  FROM generate_series(date '2022-01-01', CURRENT_DATE, interval '1 day') AS t(d)
)
SELECT
  TO_CHAR(date, 'YYYYMMDD')::int AS date_key,
  date,
  EXTRACT(YEAR FROM date)::int AS year,
  EXTRACT(MONTH FROM date)::int AS month,
  EXTRACT(DAY FROM date)::int AS day,
  EXTRACT(DOW FROM date)::int AS weekday
FROM dates
