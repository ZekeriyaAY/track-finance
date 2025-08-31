# Track Finance

Track Finance is a web application designed to help you track your personal finances, cash flow, and investments. The project is built with Flask and PostgreSQL and is deployed using a modern CI/CD workflow with Docker and GitHub Actions.

## Features

- Cash Flow Tracking
- Investment Portfolio Management
- Category and Tag-Based Reporting
- Data Import from Excel
- Multi-language Support (TR/EN)

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

---

## Development Environment Setup

For local development, this project uses `docker-compose.override.yml` to enable features like live-reloading. Docker Compose automatically detects and uses this file.

1.  **Set Up Environment Variables:**
    Create your local environment file from the template.
    ```bash
    cp .env.example .env
    ```
    Open the `.env` file and update the variables, especially `POSTGRES_PASSWORD` and `SECRET_KEY`.

2.  **Launch the Development Server:**
    This command will build the `app` image locally and start all services.
    ```bash
    docker compose up --build
    ```
    Thanks to the `docker-compose.override.yml` file, any changes you make to the Python code will automatically restart the server.

3.  **Access the Services:**
    - **Track Finance App:** [http://localhost:5001](http://localhost:5001)
    - **pgAdmin (Database Management):** [http://localhost:5050](http://localhost:5050)

### pgAdmin Setup

When you first access the pgAdmin interface at `http://localhost:5050`, you do not need to add the database server manually; the connection is created for you automatically.

-   Use the `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD` values from your `.env` file to log in.
-   You will see a "Track Finance DB" connection under "Servers" in the left-hand menu.
-   When you click on the connection, it will prompt you for the database password. Enter the `POSTGRES_PASSWORD` value from your `.env` file to access the database.

---

## Production Deployment (CI/CD Workflow)

This project is configured for Continuous Integration and Continuous Deployment (CI/CD) using GitHub Actions.

### How It Works

1.  **Push to `master`:** Every time you push a change to the `master` branch, a GitHub Action is automatically triggered.
2.  **Build & Push Image:** The action builds a new Docker image for the application and pushes it to the GitHub Container Registry (GHCR).
3.  **Deploy on Server:** You can then pull this new image on your server and restart the application with zero downtime.

### Server Deployment Steps

1.  **Initial Setup:**
    - Clone the repository to your server.
    - Create a `.env` file with your production secrets.
    - Log in to GHCR on your server: `echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin`

2.  **Deploying an Update:**
    After pushing your changes to `master` and waiting for the GitHub Action to complete:
    ```bash
    # Pull the latest application image from GHCR
    docker compose pull app

    # Restart the services with the new image
    docker compose up -d
    ```
    This process does not require you to pull the source code to the server or build the image there, making deployments fast and reliable.

## Stopping the Application

To stop all running services, execute the following command:
```bash
docker compose down
```
This command stops and removes the containers but preserves your database data stored in Docker volumes.