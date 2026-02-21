.PHONY: dev dev-d prod prod-pull up down logs logs-app clean ps help test test-report test-cov test-local test-security

# Development mode with hot-reload
dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Development mode in background
dev-d:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d

# Production mode (default)
prod:
	docker compose up -d

# Production with pull latest image
prod-pull:
	docker compose pull app
	docker compose up -d

# Generic up (production)
up:
	docker compose up -d

# Stop all services
down:
	docker compose down

# View logs
logs:
	docker compose logs -f

# View app logs only
logs-app:
	docker compose logs -f app

# Clean everything (⚠️ deletes data)
clean:
	docker compose down -v
	docker system prune -f

# Show running containers
ps:
	docker compose ps

# Run tests in Docker
test:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml exec app pytest

# Run tests with HTML report in Docker
test-report:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml exec app pytest --html=tests/report.html --self-contained-html -v

# Run tests with coverage in Docker
test-cov:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml exec app pytest --cov=. --cov-report=html

# Run tests locally
test-local:
	pytest tests/ -v

# Run security tests only
test-security:
	pytest tests/security/ -v

# Help
help:
	@echo "Track Finance - Docker Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start development mode with hot-reload"
	@echo "  make dev-d        - Start development mode in background"
	@echo ""
	@echo "Production:"
	@echo "  make prod         - Start production mode"
	@echo "  make prod-pull    - Pull latest image and start production"
	@echo ""
	@echo "Management:"
	@echo "  make down         - Stop all services"
	@echo "  make logs         - View all logs"
	@echo "  make logs-app     - View app logs only"
	@echo "  make ps           - Show running containers"
	@echo "  make clean        - Stop and remove everything (⚠️ deletes data)"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run tests in Docker"
	@echo "  make test-report   - Run tests and generate HTML report (tests/report.html)"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo "  make test-local    - Run tests locally"
	@echo "  make test-security - Run security tests only"
