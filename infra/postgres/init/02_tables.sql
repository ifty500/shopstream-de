-- Landing tables for source data. One row per source entity, upserted on the
-- source id so re-running the pipeline is idempotent. `payload` keeps the full
-- source record so nothing is lost if we later need another field.

CREATE TABLE IF NOT EXISTS raw.users (
  id_src         INT PRIMARY KEY,
  name           TEXT,
  email          TEXT,
  gender         TEXT,
  city           TEXT,
  payload        JSONB,
  ingested_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.products (
  id_src       INT PRIMARY KEY,
  title        TEXT,
  category     TEXT,
  price        NUMERIC(12,2),
  brand        TEXT,
  description  TEXT,
  payload      JSONB,
  ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.orders (
  id_src            INT PRIMARY KEY,
  user_id_src       INT NOT NULL,
  total_amount      NUMERIC(12,2),
  discounted_total  NUMERIC(12,2),
  product_count     INT,   -- distinct products in the order
  item_count        INT,   -- total units across all products
  order_date        DATE,  -- not provided by DummyJSON; see stg_orders
  payload           JSONB,
  ingested_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.order_items (
  order_id_src           INT NOT NULL,
  product_id_src         INT NOT NULL,
  quantity               INT,
  price                  NUMERIC(12,2),
  line_total             NUMERIC(12,2),
  discounted_line_total  NUMERIC(12,2),
  ingested_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (order_id_src, product_id_src)
);
