# Finance Tracker Docker Commands
.PHONY: help build up down logs restart clean migrate shell backup update dbadmin

# Load environment variables
include .env.docker
export

help: ## Show this help message
	@echo "Finance Tracker Docker Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build the Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d
	@echo "🚀 Finance Tracker is starting..."
	@echo "📱 Web app: http://localhost:$(WEB_PORT)"
	@echo "🗄️  Database: PostgreSQL on port 5432"
	@echo "🔧 Database Admin: http://localhost:$(PGADMIN_PORT)"

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
	docker-compose exec db pg_dump -U $(POSTGRES_USER) $(POSTGRES_DB) > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup completed: backup_$(shell date +%Y%m%d_%H%M%S).sql"

init: ## Initialize the application (first time setup)
	@echo "🔧 Initializing Finance Tracker..."
	make build
	make up
	sleep 10
	make migrate
	@echo "✅ Finance Tracker initialized successfully!"
	@echo "📱 Web app: http://localhost:$(WEB_PORT)"
	@echo "🗄️  Database: PostgreSQL on port 5432"
	@echo "🔧 Database Admin: http://localhost:$(PGADMIN_PORT)"
	@echo "🌐 Visit: http://localhost:$(WEB_PORT)"

update: ## Update running containers with latest configuration  
	@echo "🔄 Updating containers with latest configuration..."
	docker-compose up -d --force-recreate
	@echo "✅ Containers updated successfully!"
	@echo "📱 Web app: http://localhost:$(WEB_PORT)"
	@echo "🗄️  Database: PostgreSQL on port 5432"
	@echo "🔧 Database Admin: http://localhost:$(PGADMIN_PORT)"

dbadmin: ## Open database admin interface in browser
	@echo "🔧 Opening pgAdmin interface..."
	@echo "📊 pgAdmin: http://localhost:$(PGADMIN_PORT)"
	@echo "🗄️  Login credentials:"
	@echo "   Email: $(PGADMIN_DEFAULT_EMAIL)"
	@echo "   Password: $(PGADMIN_DEFAULT_PASSWORD)"
	@echo ""
	@echo "📋 Database connection info (add server in pgAdmin):"
	@echo "   Host: db"
	@echo "   Port: 5432"
	@echo "   Username: $(POSTGRES_USER)"
	@echo "   Password: $(POSTGRES_PASSWORD)"
	@echo "   Database: $(POSTGRES_DB)"
	@which open >/dev/null 2>&1 && open http://localhost:$(PGADMIN_PORT) || echo "🌐 Please open http://localhost:$(PGADMIN_PORT) in your browser"
