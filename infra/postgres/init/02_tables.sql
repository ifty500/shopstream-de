CREATE TABLE IF NOT EXISTS raw_users (
  id_src         INT PRIMARY KEY,
  name           TEXT,
  email          TEXT,
  gender         TEXT,
  city           TEXT,
  payload        JSONB,
  ingested_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw_products (
  id_src       INT PRIMARY KEY,
  title        TEXT,
  category     TEXT,
  price        NUMERIC(12,2),
  brand        TEXT,
  description  TEXT,
  payload      JSONB,
  ingested_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw_orders (
  id_src        INT PRIMARY KEY,
  user_id_src   INT NOT NULL,
  total_amount  NUMERIC(12,2),
  item_count    INT,
  order_date    DATE,
  payload       JSONB,
  ingested_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw_order_items (
  order_id_src    INT,
  product_id_src  INT,
  quantity        INT,
  price           NUMERIC(12,2),
  line_total      NUMERIC(12,2),
  PRIMARY KEY(order_id_src, product_id_src)
);
