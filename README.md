# Track Finance

Track Finance is a web application designed to help you track your personal finances, cash flow, and investments. The project is built with Flask and PostgreSQL and is easily deployable with Docker.

## Features

- Cash Flow Tracking
- Investment Portfolio Management
- Category and Tag-Based Reporting
- Data Import from Excel
- Multi-language Support (TR/EN)

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/) (Typically included with Docker Desktop)

## Quick Start (with Docker Compose)

This project uses Docker Compose to launch all necessary services (Application, Database, DB Management UI) with a single command.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/ZekeriyaAY/track-finance.git
    cd track-finance
    ```

2.  **Set Up Environment Variables:**
    Create your own environment configuration file by copying the example file.
    ```bash
    cp .env.example .env
    ```
    Next, open the `.env` file in a text editor and update at least the `POSTGRES_PASSWORD` and `SECRET_KEY` variables with secure values.

3.  **Launch the Application:**
    The following command will build the required Docker images and start all services in the background.
    ```bash
    docker compose up --build -d
    ```
    - `--build`: Rebuilds the image if you have made changes to the code.
    - `-d`: Runs the services in detached mode (in the background).

    You can view the logs using the `docker compose logs -f` command.

4.  **Access the Services:**
    - **Track Finance App:** [http://localhost:5001](http://localhost:5001)
    - **pgAdmin (Database Management):** [http://localhost:5050](http://localhost:5050)

## Services

### pgAdmin Setup

When you first access the pgAdmin interface at `http://localhost:5050`, you do not need to add the database server manually; the connection is created for you automatically.

-   Use the `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD` values from your `.env` file to log in.
-   You will see a "Track Finance DB" connection under "Servers" in the left-hand menu.
-   When you click on the connection, it will prompt you for the database password. Enter the `POSTGRES_PASSWORD` value from your `.env` file to access the database.

## Stopping the Application

To stop all running services, execute the following command:
```bash
docker compose down
```
This command stops and removes the containers and network created by docker compose up, but it will not delete the volumes where your data is stored.

## Production Notes

- In a production environment, it is more secure to manage environment variables directly through your deployment platform (e.g., Portainer, Kubernetes, or systemd) rather than using an `.env` file.
- It is highly recommended to disable external access to the database by commenting out or removing the ports section of the db service in docker-compose.yml.