.PHONY: up down ingest dbt logs psql

up:
	docker compose up -d --build

down:
	docker compose down -v


ingest:
	docker compose exec app python -m orchestration.flows.master_flow


dbt:
	docker compose exec app bash -lc "cd dbt_shopstream && dbt deps && dbt run && dbt test"

logs:
	docker compose logs -f --tail=200 app

psql:
	docker compose exec postgres psql -U $$POSTGRES_USER -d $$POSTGRES_DB
