help:
	@echo "help  -- print this help"
	@echo "start -- start docker stack"
	@echo "stop  -- stop docker stack"
	@echo "ps    -- show status"
	@echo "clean -- clean all artifacts"
	@echo "test  -- run tests using docker"
	@echo "dockershell -- run bash inside docker"

start:
	docker build -t mysite .
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

dockershell:
	docker compose run --rm web bash

migrations:
	docker compose run --rm web python3 manage.py makemigrations

migrate:
	docker compose run --rm web python3 manage.py migrate --skip-checks

.PHONY: help start stop ps clean test dockershell only_test pep8
