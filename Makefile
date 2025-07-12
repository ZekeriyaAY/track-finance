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
	@echo "📊 Grafana: http://localhost:$(GRAFANA_PORT)"

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

show_grafana: ## Show Grafana service status
	@echo "=== Grafana Service Status ==="
	@echo "Grafana URL: http://localhost:$(GRAFANA_PORT)"
	@echo "Admin User: $(GRAFANA_ADMIN_USER)"
	@echo "Admin Password: $(GRAFANA_ADMIN_PASSWORD)"
	@echo ""
	@docker-compose ps grafana

grafana_logs: ## Show logs for Grafana service
	@echo "=== Grafana Logs ==="
	@docker-compose logs -f grafana

restart_grafana: ## Restart the Grafana service
	@echo "=== Restarting Grafana Service ==="
	@docker-compose restart grafana

setup_grafana_views: ## Set up Grafana database views
	@echo "=== Setting up Grafana Database Views ==="
	@docker-compose exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c "\
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
	@echo "Grafana database views created successfully!"
