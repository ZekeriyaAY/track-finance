# Where's My Money? - Personal Finance Management Application

Where's My Money? is a simple and effective web application developed for personal finance management. It allows you to track your income and expenses (cash flow), categorize and tag them, and manage your investments. With the data import feature from Excel files, you can easily add your bank transactions to the system.

The project is designed to run on Docker, integrated with Grafana for data visualization and PgAdmin for database management.

## ✨ Key Features

- **Cash Flow Management:** Record and list your income and expenses.
- **Categorization and Tagging:** Create categories and tags to better analyze your spending.
- **Investment Tracking:** Manage your investments and their types.
- **Excel Import:** Import transactions from bank statements (Excel/CSV format).
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

    **CSRF Token Error Fix:**
    If you get "CSRF session token is missing" error in production, add these to your environment:
    ```env
    SESSION_COOKIE_SECURE=False
    WTF_CSRF_SSL_STRICT=False
    ```
    Only set these to `True` if you're using HTTPS. If behind a reverse proxy (nginx/traefik), also add:
    ```env
    BEHIND_PROXY=True
    PREFERRED_URL_SCHEME=https
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