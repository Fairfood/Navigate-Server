default: help

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

#Doker service commands

.PHONY: stop-all
stop-all: # Stop all running containers
	docker stop $$(docker ps -aq)

.PHONY: stop-and-remove
stop-and-remove: # Stop and remove all running containers
	docker stop $$(docker ps -aq) && docker rm $$(docker ps -aq)

.PHONY: clean-all
clean-all: # Stop all running containers, remove all containers, and clear all volumes
	docker stop $$(docker ps -aq) && docker rm $$(docker ps -aq) && docker volume rm $$(docker volume ls -q) && docker image prune


#Base commands

.PHONY: django-shell
django-shell: # Run Django shell
	docker exec -it navigate-django python3 manage.py shell

.PHONY: django-shellplus
django-shellplus: # Run Django shell_plus
	docker exec -it navigate-django python3 manage.py shell_plus

.PHONY: collect-static
collect-static: # Collect static files
	docker exec -it navigate-django python3 manage.py collectstatic

.PHONY: django-logs
django-logs: # Tail Django logs
	docker logs -f navigate-django

.PHONY: celery-logs
celery-logs: # Tail Celery logs
	docker logs -f navigate-celery

.PHONY: celery-beat-logs
celery-beat-logs: # Tail Celery Beat logs
	docker logs -f navigate-celerybeat

.PHONY: run-tests
run-tests: # Run tests
	docker exec -it navigate-django python3 manage.py test

.PHONY: make-migrations
make-migrations: # Make database migrations
	docker exec -it navigate-django python3 manage.py makemigrations

.PHONY: migrate
migrate: # Apply database migrations
	docker exec -it navigate-django python3 manage.py migrate

.PHONY: flush-db
flush-db: # Flush the django database
	docker exec -it navigate-django python3 manage.py flush --noinput

.PHONY: pg-shell
pg-shell: # Command to run an interactive shell in the PostgreSQL container
	docker exec -it navigate-postgres sh

.PHONY: up
up: # Bring up the local environment
	docker compose -f docker-compose.yml up

.PHONY: up-build
up-build: # Build and bring up the local environment
	docker compose -f docker-compose.yml up --build

.PHONY: build-django
build-django: # Build the Django service without cache
	docker compose -f docker-compose.yml build navigate-django --no-cache

.PHONY: down
down: # Bring down the local environment
	docker compose -f docker-compose.yml down

.PHONY: connect-django
connect-django: # Connect django project environment
	docker exec -it navigate-django bash