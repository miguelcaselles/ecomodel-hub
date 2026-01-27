.PHONY: help up down logs shell db-shell migrate seed test clean

help:
	@echo "EcoModel Hub - Comandos disponibles:"
	@echo "  make up          - Levantar todos los servicios"
	@echo "  make down        - Parar todos los servicios"
	@echo "  make logs        - Ver logs en tiempo real"
	@echo "  make shell       - Abrir shell en contenedor backend"
	@echo "  make db-shell    - Abrir psql en base de datos"
	@echo "  make migrate     - Ejecutar migraciones"
	@echo "  make seed        - Cargar datos de demo"
	@echo "  make test        - Ejecutar tests"
	@echo "  make clean       - Limpiar contenedores y volúmenes"

up:
	cd docker && docker compose up -d
	@echo "✓ Servicios iniciados"
	@echo "  API: http://localhost:8001/api/v1/docs"
	@echo "  Frontend: http://localhost:3001"

down:
	cd docker && docker compose down
	@echo "✓ Servicios detenidos"

logs:
	cd docker && docker compose logs -f

logs-backend:
	cd docker && docker compose logs -f backend

logs-celery:
	cd docker && docker compose logs -f celery_worker

shell:
	cd docker && docker compose exec backend bash

db-shell:
	cd docker && docker compose exec db psql -U ecomodel -d ecomodel

migrate:
	cd docker && docker compose exec backend alembic upgrade head
	@echo "✓ Migraciones ejecutadas"

migrate-create:
	@read -p "Nombre de la migración: " name; \
	cd docker && docker compose exec backend alembic revision --autogenerate -m "$$name"

seed:
	cd docker && docker compose exec backend python seed_data.py
	@echo "✓ Datos de demo cargados"

test:
	cd docker && docker compose exec backend pytest

clean:
	cd docker && docker compose down -v
	@echo "✓ Contenedores y volúmenes eliminados"

restart:
	cd docker && docker compose restart
	@echo "✓ Servicios reiniciados"

build:
	cd docker && docker compose build
	@echo "✓ Imágenes reconstruidas"
