.PHONY: help up down restart logs clean install test

help:
	@echo "Anaya Watchtower - Makefile Commands"
	@echo "======================================"
	@echo "make up          - Start all services"
	@echo "make down        - Stop all services"
	@echo "make restart     - Restart all services"
	@echo "make logs        - View logs (all services)"
	@echo "make logs-backend - View backend logs only"
	@echo "make clean       - Remove volumes and clean up"
	@echo "make install     - Install backend dependencies"
	@echo "make migrate     - Run database migrations"
	@echo "make test        - Run tests"
	@echo "make shell       - Open backend shell"

up:
	docker-compose up -d
	@echo "✅ Services started. Backend: http://localhost:8080"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-postgres:
	docker-compose logs -f postgres

logs-redis:
	docker-compose logs -f redis

clean:
	docker-compose down -v
	@echo "✅ Volumes cleaned"

install:
	cd backend && pip install -r requirements.txt

migrate:
	docker-compose exec backend python -c "from db.migrations import run_migrations; import asyncio; asyncio.run(run_migrations())"

shell:
	docker-compose exec backend /bin/bash

psql:
	docker-compose exec postgres psql -U anaya -d anaya_watchtower

redis-cli:
	docker-compose exec redis redis-cli

test:
	cd backend && pytest tests/ -v

build:
	docker-compose build --no-cache

rebuild: down clean build up
	@echo "✅ Full rebuild complete"
