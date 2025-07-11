# Finance Tracker Docker Commands
.PHONY: help build up down logs restart clean migrate shell backup setup dev pgadmin update init-db status setup_grafana

# Load environment variables
include .env
export

help: ## Show this help message
	@echo "Finance Tracker Docker Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Main commands
setup: ## First time setup (copies .env.example and starts services)
	@echo "🔧 Setting up Finance Tracker..."
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env from template..."; \
		cp .env.example .env; \
		echo "⚠️  Please edit .env file with your settings before running 'make up'"; \
	else \
		echo "✅ .env file already exists"; \
		make build; \
		make up; \
		sleep 10; \
		make migrate; \
		make setup_grafana; \
		@echo "✅ Finance Tracker initialized successfully!"; \
		@echo "📱 Web app: http://localhost:$(WEB_PORT)"; \
		@echo "🔧 Database Admin: http://localhost:$(PGADMIN_PORT)"; \
		@echo "📊 Grafana: http://localhost:$(GRAFANA_PORT)"; \
	fi

build: ## Build the Docker images
	docker-compose build

up: ## Start all services (production mode)
	docker-compose up -d
	@echo "🚀 Finance Tracker is starting..."
	@echo "📱 Web app: http://localhost:$(WEB_PORT)"
	@echo "🔧 Database Admin: http://localhost:$(PGADMIN_PORT)"
	@echo "📊 Grafana: http://localhost:$(GRAFANA_PORT)"
	@echo ""
	@echo "⚠️  Don't forget to run migrations if needed: make migrate"

dev: ## Start with debug mode enabled
	FLASK_ENV=development FLASK_DEBUG=1 docker-compose up -d
	@echo "🚀 Finance Tracker is starting in DEBUG MODE..."
	@echo "📱 Web app: http://localhost:$(WEB_PORT) (debug enabled)"
	@echo "🔧 Database Admin: http://localhost:$(PGADMIN_PORT)"
	@echo "📊 Grafana: http://localhost:$(GRAFANA_PORT)"
	@echo ""
	@echo "⚠️  Debug mode is ENABLED - detailed error messages will be shown"
	@echo "🔄 Running database migrations..."
	@sleep 10
	@make migrate || echo "⚠️  Migration failed - database might not be ready yet. Try: make migrate"
	@echo "✅ Debug environment ready!"

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

# Database commands
init-db: ## Initialize database and migrations (first time only)
	docker-compose exec web flask db init
	docker-compose exec web flask db migrate -m "Initial migration"
	docker-compose exec web flask db upgrade

migrate: ## Run database migrations
	docker-compose exec web flask db upgrade

backup: ## Backup the database
	@echo "Creating database backup..."
	docker-compose exec db pg_dump -U $(POSTGRES_USER) $(POSTGRES_DB) > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup completed: backup_$(shell date +%Y%m%d_%H%M%S).sql"

# Utility commands
status: ## Show status of all services
	@echo "=== Finance Tracker Services Status ==="
	@echo ""
	@docker-compose ps
	@echo ""
	@echo "=== Health Checks ==="
	@echo "🔍 Web App Health:"
	@curl -s http://localhost:$(WEB_PORT)/health 2>/dev/null && echo " ✅ Web app is healthy" || echo " ❌ Web app is not responding"
	@echo "🔍 Database Connection:"
	@docker-compose exec -T db pg_isready -U $(POSTGRES_USER) -d $(POSTGRES_DB) 2>/dev/null && echo " ✅ Database is ready" || echo " ❌ Database is not ready"
	@echo "🔍 Grafana:"
	@curl -s http://localhost:$(GRAFANA_PORT)/api/health 2>/dev/null | grep -q "ok" && echo " ✅ Grafana is healthy" || echo " ❌ Grafana is not responding"
	@echo "🔍 pgAdmin:"
	@curl -s http://localhost:$(PGADMIN_PORT)/misc/ping 2>/dev/null && echo " ✅ pgAdmin is healthy" || echo " ❌ pgAdmin is not responding"

shell: ## Open a shell in the web container
	docker-compose exec web bash

pgadmin: ## Open pgAdmin interface in browser
	@echo "🔧 Opening pgAdmin interface..."
	@echo "📊 pgAdmin: http://localhost:$(PGADMIN_PORT)"
	@echo "🗄️  Login: $(PGADMIN_DEFAULT_EMAIL) / $(PGADMIN_DEFAULT_PASSWORD)"
	@which open >/dev/null 2>&1 && open http://localhost:$(PGADMIN_PORT) || echo "🌐 Please open http://localhost:$(PGADMIN_PORT) in your browser"

update: ## Update running containers with latest configuration
	@echo "🔄 Updating containers..."
	docker-compose up -d --force-recreate
	@echo "✅ Containers updated successfully!"

# Grafana commands
setup_grafana: ## Set up Grafana database views and configuration
	@echo "=== Setting up Grafana for Finance Tracker ==="
	@docker cp grafana/sql/views.sql $$(docker-compose ps -q db):/tmp/views.sql
	@docker-compose exec -T db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -f /tmp/views.sql
	@echo "✅ Grafana database views created successfully!"
	@echo "📊 Grafana: http://localhost:$(GRAFANA_PORT)"
	@echo "🔑 Login: $(GRAFANA_ADMIN_USER) / $(GRAFANA_ADMIN_PASSWORD)"
