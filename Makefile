help:
	@echo "help  -- print this help"
	@echo "start -- start docker stack"
	@echo "stop  -- stop docker stack"
	@echo "ps    -- show status"
	@echo "clean -- clean all artifacts"
	@echo "test  -- run tests using docker"
	@echo "webshell -- run bash inside web container"
	@echo "dbshell -- run bash inside db container"
	@echo "migrations -- make migrations"
	@echo "migrate -- migrate"

start:
	TARGET=development docker build .
	docker compose up

stop:
	docker compose stop

ps:
	docker compose ps

clean: stop
	docker compose rm --force -v

only_test:
	docker compose run --rm web /usr/local/bin/pytest -v

pep8:
	docker compose run --rm web flake8

test: pep8 only_test

# attach to a new container
webshell:
	docker compose run --rm web bash

# attach to running container
ssh:
	docker compose exec web bash

dbshell:
	docker compose exec db psql --username=carlos --dbname=my_site_prod

migrations:
	docker compose run --rm web python3 manage.py makemigrations

migrate:
	docker compose run --rm web python3 manage.py migrate --skip-checks

.PHONY: help start stop ps clean test webshell dbshell migrations migrate only_test pep8
