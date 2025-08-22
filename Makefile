ifneq (,$(wildcard .env))
    include .env
    export
endif

TIMESTAMP := $(shell date +%Y-%m-%d-%H%M%S)

UVR=uv run

help:
	@echo "DATABASE_URL = $(DATABASE_URL)"
	@echo "help        -- Show this help message"
	@echo "start       -- Build and start the Docker stack"
	@echo "stop        -- Stop the Docker stack"
	@echo "ps          -- Show the status of the containers in the Docker stack"
	@echo "clean       -- Stop and remove all Docker containers, networks, and volumes"
	@echo "test        -- Run tests (including PEP8 check and unit tests)"
	@echo "webshell    -- Open a new Bash shell in the web container"
	@echo "ssh         -- Attach to a running web container and open a Bash shell"
	@echo "dbshell     -- Open a psql shell inside the database container"
	@echo "migrations  -- Create new database migrations"
	@echo "migrate     -- Apply the database migrations"
	@echo "dbdump      -- Dump the database to a file, with timestamp"
	@echo "dbrunsql    -- Run a .sql file (can also restore the db from a dbdump file)"

start:
	TARGET=development docker compose up --build

stop:
	docker compose stop

ps:
	docker compose ps

clean: stop
	docker compose rm --force -v

only_test:
	docker compose run --rm -e TESTING=True web ${UVR} pytest -v

pep8:
	docker compose run --rm web ${UVR} ruff check

test: pep8 only_test

# attach to a new container
webshell:
	docker compose run --rm web bash

# attach to running container
ssh:
	docker compose exec web bash

dbshell:
	docker compose exec db psql $(DATABASE_URL)

dbdump:
	docker compose exec db pg_dump $(DATABASE_URL) > cacrespo-dbdump-$(TIMESTAMP).sql

dbrunsql:
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify the file using FILE=filename.sql"; \
		exit 1; \
	fi
	cat $(FILE) | docker compose exec -T db psql $(DATABASE_URL)

migrations:
	docker compose run --rm web ${UVR} manage.py makemigrations

migrate:
	docker compose run --rm web ${UVR} manage.py migrate --skip-checks

.PHONY: help start stop ps clean test webshell dbshell migrations migrate only_test pep8 dbdump dbrunsql
