# Track Finance

Track Finance is a simple and effective web application developed for personal finance management. It allows you to track your income and expenses (cash flow), categorize and tag them, and manage your investments. With the data import feature from Excel files, you can easily add your bank transactions to the system.

The project is designed to run on Docker, integrated with Grafana for data visualization and PgAdmin for database management.

## ✨ Key Features

- **Cash Flow Management:** Record and list your income and expenses.
- **Categorization and Tagging:** Create categories and tags to better analyze your spending.
- **Investment Tracking:** Manage your investments and their types.
- **Import from Excel:** Automatically record transactions by uploading your bank statements (in Excel format).
- **Visualization:** Monitor your financial data with visual dashboards through Grafana integration.

##  Setup and Run

The project can be easily run using Docker and Docker Compose.

1.  **Clone the Project:**
    ```bash
    git clone https://github.com/ZekeriyaAY/track-finance.git
    cd track-finance
    ```

2.  **Set Up Environment Variables (Optional):**
    You can create a `.env` file in the project root to customize passwords and settings, or edit them directly in `docker-compose.yml`.

    ```env
    POSTGRES_PASSWORD=change_me
    SECRET_KEY=very-secret-key
    PGADMIN_DEFAULT_EMAIL=admin@admin.com
    PGADMIN_DEFAULT_PASSWORD=admin
    GRAFANA_ADMIN_USER=admin
    GRAFANA_ADMIN_PASSWORD=admin
    ```

3.  **Run:**
    ```bash
    # Production mode
    make prod
    # or
    docker compose up -d
    
    # Development mode with hot-reload
    make dev
    # or
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
    ```

## 🌐 Access

- **Application:** [http://localhost:5001](http://localhost:5001)
- **PgAdmin:** [http://localhost:5050](http://localhost:5050)
- **Grafana:** [http://localhost:3000](http://localhost:3000)

Use the credentials defined in your `.env` file or the defaults from `docker-compose.yml`.

## 📝 Useful Commands

```bash
make down         # Stop all services
make logs         # View all logs
make logs-app     # View app logs only
make ps           # Show running containers
make clean        # Remove everything (⚠️ deletes data)
```