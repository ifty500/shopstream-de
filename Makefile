.PHONY: up down clean ingest dbt test dashboard docs demo logs psql

up:            ## Build and start all services
	docker compose up -d --build

down:          ## Stop services (keeps data)
	docker compose down

clean:         ## Stop services and delete all data volumes
	docker compose down -v

ingest:        ## Run the full Prefect pipeline: extract -> validate -> load -> dbt build
	docker compose exec app python -m orchestration.flows.master_flow

dbt:           ## Run dbt models and tests only
	docker compose exec app bash -lc "cd dbt_shopstream && dbt build --profiles-dir ."

test:          ## Run Python unit tests
	docker compose exec app python -m pytest -q tests

dashboard:     ## Create the Metabase admin user, DB connection and demo dashboard
	docker compose exec app python -m scripts.metabase_setup

docs:          ## Generate dbt docs and serve them on http://localhost:8081
	docker compose exec app bash -lc "cd dbt_shopstream && dbt docs generate --profiles-dir . && python -m http.server 8080 --bind 0.0.0.0 --directory target"

demo: up ingest dashboard  ## Everything needed for a demo, from scratch
	@echo ""
	@echo "Metabase dashboard: http://localhost:3000"
	@echo "Prefect UI:         http://localhost:4200"
	@echo "dbt docs:           run 'make docs', then open http://localhost:8081"

logs:
	docker compose logs -f --tail=200 app

psql:          ## Open a psql shell in the Postgres container
	docker compose exec postgres sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'
