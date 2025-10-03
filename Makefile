.PHONY: dev dev-d prod prod-pull up down logs logs-app clean ps help

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
