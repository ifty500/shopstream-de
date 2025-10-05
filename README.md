# ShopStream DE — Modern Local Data Engineering Environment

A production-grade local data engineering environment that demonstrates modern data practices and tools.

## 🛠 Tech Stack

- **Orchestration:** Prefect 2
- **Storage:** PostgreSQL
- **Transformation:** dbt Core
- **Data Quality:** Great Expectations
- **Visualization:** Metabase
- **Infrastructure:** Docker Compose
- **Source:** DummyJSON API (users, orders, products) – no authentication required

## 🚀 Quickstart

1. Clone and setup environment:
```bash
# Clone repository
git clone [repo-url]
cd shopstream-de

# Setup environment
cp .env.example .env        # Copy environment template
```

2. Start the services:
```bash
docker compose up -d        # Launch PostgreSQL, Metabase, and application
```

3. Run the pipeline:
```bash
make ingest                 # Full pipeline: extract → validate → transform
make dbt                    # Optional: Run dbt transforms separately
```

## 🔌 Service Access

- **Metabase:** [http://localhost:3000](http://localhost:3000)
  - First time setup required
  - Use database credentials from `.env`

- **PostgreSQL:**
  - Host: localhost
  - Port: 5437 (external)
  - Internal host: postgres (for services within Docker network)
  - Credentials: See `.env` file

## 📊 Data Pipeline

1. **Extraction:** 
   - Sources data from DummyJSON API
   - Loads users, products, and orders into `raw.*` schema

2. **Validation:**
   - Implements Great Expectations checks
   - Fails fast if data quality issues detected
   - Configurable validation rules

3. **Transformation:**
   - Uses dbt for data modeling
   - Creates a star schema:
     - Dimension tables: `dim_users`, `dim_products`, `dim_date`
     - Fact tables: `fact_orders`, `fact_order_items`
   - Implements staging layer (`stg.*`) for data cleaning

## ⚙️ Available Commands

```bash
make up         # Start all services
make down       # Stop services and remove volumes
make ingest     # Run complete Prefect pipeline
make dbt        # Execute dbt transformations and tests
```

## 📁 Project Structure

```
shopstream-de/
├── dbt_shopstream/           # DBT project
│   ├── models/              # Data models
│   │   ├── marts/          # Business-level tables
│   │   └── staging/        # Cleaned raw data
│   └── tests/              # Data tests
├── great_expectations/      # Data quality configs
├── infra/                   # Infrastructure
│   └── postgres/           # Database initialization
├── orchestration/          # Prefect flows
│   └── flows/             # Pipeline definitions
└── pipelines/             # Core pipeline code
    ├── extract/          # Data extraction
    ├── load/            # Data loading
    └── quality/         # Quality checks
```

## 🔒 Security Notes

- Sensitive information is managed through environment variables
- Default credentials are for development only
- Production deployments should use secure credentials
- `.env` file is excluded from version control

## 💡 Advanced Features

- **Idempotent Operations:** Safe to re-run pipelines
- **Error Handling:** Retries and failure management
- **Type Safety:** Strongly typed database schemas
- **Testing:** Comprehensive dbt and data quality tests
- **Monitoring:** Pipeline observability with Prefect

## 🚧 Future Improvements

- DuckDB support for local development
- Extended data quality checks
- Additional data sources
- Enhanced testing coverage
- Metrics and monitoring dashboards
