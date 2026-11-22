-- Handy queries for a live walkthrough (make psql, then paste).

-- 1. Row counts through each layer
SELECT 'raw.orders' AS layer, count(*) FROM raw.orders
UNION ALL SELECT 'stg.stg_orders', count(*) FROM stg.stg_orders
UNION ALL SELECT 'mart.fact_orders', count(*) FROM mart.fact_orders
UNION ALL SELECT 'mart.fact_order_items', count(*) FROM mart.fact_order_items;

-- 2. Revenue and discount by category
SELECT p.category,
       SUM(i.quantity)                                AS units,
       ROUND(SUM(i.line_total), 2)                    AS gross,
       ROUND(SUM(i.discounted_line_total), 2)         AS revenue,
       ROUND(100 * (1 - SUM(i.discounted_line_total) / NULLIF(SUM(i.line_total), 0)), 1) AS discount_pct
FROM mart.fact_order_items i
JOIN mart.dim_products p ON p.product_key = i.product_key
GROUP BY 1
ORDER BY revenue DESC;

-- 3. Top customers
SELECT u.name, u.city, COUNT(*) AS orders, ROUND(SUM(f.discounted_total), 2) AS revenue
FROM mart.fact_orders f
JOIN mart.dim_users u ON u.user_key = f.user_key
GROUP BY 1, 2
ORDER BY revenue DESC
LIMIT 10;

-- 4. Raw payload is kept: pull a field we never modelled
SELECT id_src, payload->'company'->>'title' AS job_title
FROM raw.users
LIMIT 5;

-- 5. Idempotency check: re-run `make ingest`, then confirm there are still no duplicates
SELECT order_item_key, count(*) FROM mart.fact_order_items GROUP BY 1 HAVING count(*) > 1;
