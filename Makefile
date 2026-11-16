# =============================================================================
# RedLink – Blood Bank Management & Hemovigilance System
# Makefile — common developer commands
# =============================================================================

.PHONY: help run migrate makemigrations test seed shell static collectstatic \
        docker-up docker-down docker-logs docker-build lint format clean

# Default target
help:
	@echo ""
	@echo "  RedLink – Hemovigilance System  "
	@echo "=================================="
	@echo ""
	@echo "  Development:"
	@echo "    make run            Start development server"
	@echo "    make shell          Open Django shell"
	@echo "    make migrate        Apply database migrations"
	@echo "    make makemigrations Create new migrations"
	@echo "    make seed           Seed demo / test data"
	@echo "    make static         Collect static files"
	@echo ""
	@echo "  Testing:"
	@echo "    make test           Run all tests"
	@echo "    make test-cov       Run tests with coverage report"
	@echo "    make lint           Run flake8 linter"
	@echo "    make format         Auto-format with black"
	@echo ""
	@echo "  Docker:"
	@echo "    make docker-up      Start all containers (detached)"
	@echo "    make docker-down    Stop and remove containers"
	@echo "    make docker-build   Rebuild Docker images"
	@echo "    make docker-logs    Stream container logs"
	@echo ""
	@echo "  Utilities:"
	@echo "    make clean          Remove .pyc, __pycache__, coverage files"
	@echo ""

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------
run:
	python manage.py runserver

shell:
	python manage.py shell

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

seed:
	python manage.py seed_demo_data

static:
	python manage.py collectstatic --noinput

# ---------------------------------------------------------------------------
# Testing & Code Quality
# ---------------------------------------------------------------------------
test:
	python manage.py test --verbosity=2

test-cov:
	coverage run manage.py test --verbosity=2
	coverage report -m
	coverage html
	@echo "HTML report: htmlcov/index.html"

lint:
	flake8 . --max-line-length=120 --exclude=migrations,staticfiles,venv

format:
	black . --exclude="/(migrations|staticfiles|venv)/"

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------
docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-build:
	docker compose build

docker-logs:
	docker compose logs -f

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/ .pytest_cache/
	@echo "Cleaned."
