# Finance Tracker Docker Commands
.PHONY: help build up down logs restart clean migrate shell backup setup dev pgadmin update init-db

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
setup_grafana_views: ## Set up Grafana database views
	@echo "=== Setting up Grafana Database Views ==="
	@docker-compose exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -f /dev/stdin <<< "\
		DROP VIEW IF EXISTS grafana_monthly_summary CASCADE; \
		DROP VIEW IF EXISTS grafana_category_trends CASCADE; \
		DROP VIEW IF EXISTS grafana_investment_performance CASCADE; \
		DROP VIEW IF EXISTS grafana_cashflow_analysis CASCADE; \
		CREATE VIEW grafana_monthly_summary AS \
		SELECT DATE_TRUNC('month', date) as month, \
			SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_income, \
			SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as total_expenses, \
			SUM(amount) as net_cashflow, \
			COUNT(*) as transaction_count \
		FROM cashflow GROUP BY DATE_TRUNC('month', date) ORDER BY month; \
		CREATE VIEW grafana_category_trends AS \
		SELECT c.name as category_name, \
			DATE_TRUNC('month', cf.date) as month, \
			SUM(CASE WHEN cf.amount < 0 THEN ABS(cf.amount) ELSE 0 END) as expenses, \
			SUM(CASE WHEN cf.amount > 0 THEN cf.amount ELSE 0 END) as income, \
			COUNT(*) as transaction_count \
		FROM cashflow cf JOIN category c ON cf.category_id = c.id \
		GROUP BY c.name, DATE_TRUNC('month', cf.date) ORDER BY month, category_name; \
		CREATE VIEW grafana_investment_performance AS \
		SELECT i.name as investment_name, it.name as investment_type, \
			i.purchase_price, i.current_value, \
			(i.current_value - i.purchase_price) as profit_loss, \
			CASE WHEN i.purchase_price > 0 THEN ((i.current_value - i.purchase_price) / i.purchase_price) * 100 ELSE 0 END as profit_loss_percentage, \
			i.purchase_date, i.created_at \
		FROM investment i JOIN investment_type it ON i.investment_type_id = it.id ORDER BY i.purchase_date; \
		CREATE VIEW grafana_cashflow_analysis AS \
		SELECT cf.id, cf.date, cf.amount, cf.description, c.name as category_name, \
			CASE WHEN cf.amount > 0 THEN 'Income' ELSE 'Expense' END as transaction_type, \
			ABS(cf.amount) as absolute_amount, \
			DATE_PART('year', cf.date) as year, DATE_PART('month', cf.date) as month, \
			DATE_PART('day', cf.date) as day, TO_CHAR(cf.date, 'Day') as day_of_week, \
			cf.created_at \
		FROM cashflow cf JOIN category c ON cf.category_id = c.id ORDER BY cf.date DESC;"
	@echo "✅ Grafana database views created successfully!"
