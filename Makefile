# Finance Tracker Docker Commands
.PHONY: help build up down logs restart clean migrate shell backup update

help: ## Show this help message
	@echo "Finance Tracker Docker Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build the Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d
	@echo "🚀 Finance Tracker is starting..."
	@echo "📱 Web app: http://localhost:5001"
	@echo "🗄️  Database: PostgreSQL on port 5432"

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

restart: ## Restart all services
	docker-compose down
	docker-compose up -d

clean: ## Remove all containers, networks, and volumes
	docker-compose down -v --rmi all
	docker system prune -f

migrate: ## Run database migrations
	docker-compose exec web flask db upgrade

shell: ## Open a shell in the web container
	docker-compose exec web bash

backup: ## Backup the database
	@echo "Creating database backup..."
	docker-compose exec db pg_dump -U finance_user finance_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup completed: backup_$(shell date +%Y%m%d_%H%M%S).sql"

init: ## Initialize the application (first time setup)
	@echo "🔧 Initializing Finance Tracker..."
	make build
	make up
	sleep 10
	make migrate
	@echo "✅ Finance Tracker initialized successfully!"
	@echo "🌐 Visit: http://localhost:5001"

update: ## Update server with latest code changes
	@echo "🔄 Updating Finance Tracker..."
	@echo "📦 Creating backup..."
	-make backup
	@echo "⬇️  Pulling latest changes..."
	git pull origin main
	@echo "🔨 Rebuilding containers..."
	make down
	docker-compose build --no-cache
	make up
	@echo "⏳ Waiting for containers..."
	sleep 10
	@echo "🗄️  Running migrations..."
	-make migrate
	@echo "✅ Update completed!"
	@echo "🌐 App running at: http://$$(hostname -I | awk '{print $$1}'):5001"
	@make logs
