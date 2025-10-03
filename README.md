# Track Finance

Track Finance is a production-ready web application designed to help you track your personal finances, cash flow, and investments. The project is built with Flask and PostgreSQL and is optimized for modern container deployments with Docker, and GitHub Actions CI/CD.

## Features

- 💰 Cash Flow Tracking
- 📈 Investment Portfolio Management
- 🏷️ Category and Tag-Based Reporting
- 📊 Data Import from Excel Files
- 📋 Grafana Analytics Integration
- 🐳 Production-Ready Docker Deployment

## Prerequisites

- [Docker](https://www.docker.com/get-started) (24.0+ recommended)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+ recommended)

## Quick Start

### 🔧 Development Mode (Local with hot-reload)

```bash
# Clone the repository
git clone https://github.com/ZekeriyaAY/track-finance.git
cd track-finance

# Start development mode
make dev

# Services will be available at:
# - Track Finance App: http://localhost:5001
# - pgAdmin: http://localhost:5050 (admin@admin.com / admin)
# - Grafana: http://localhost:3000 (admin / admin)
```

### 🚀 Production Mode (Server deployment)

```bash
# Start production mode (uses pre-built GHCR image)
make prod

# Or manually with docker compose
docker compose up -d
```

### 🔒 Production Security Setup (Recommended)

For production environments, override the default passwords:

```bash
# Option 1: Environment variables (Portainer-compatible)
export POSTGRES_PASSWORD="your_secure_password"
export SECRET_KEY="your_32_char_secret_key" 
export PGADMIN_DEFAULT_PASSWORD="your_pgadmin_password"
export GRAFANA_ADMIN_PASSWORD="your_grafana_password"

# Option 2: Create .env file
cat > .env << EOF
POSTGRES_PASSWORD=your_secure_password
SECRET_KEY=your_32_char_secret_key
PGADMIN_DEFAULT_PASSWORD=your_pgadmin_password
GRAFANA_ADMIN_PASSWORD=your_grafana_password
FLASK_ENV=production
EOF

# Generate secure passwords
openssl rand -hex 32  # For SECRET_KEY
openssl rand -hex 16  # For database passwords
```

---

## Docker Compose Usage

This project uses a clean two-mode Docker setup:

### � **Production Mode** (Default - no flags needed)
```bash
# Clean command - uses base docker-compose.yml
docker compose up -d

# Or pull latest and start
docker compose pull app
docker compose up -d

# Features:
# ✅ Pre-built GHCR image (ghcr.io/zekeriyaay/track-finance:latest)
# ✅ Gunicorn production server
# ✅ Production security settings
# ✅ No volume mounting
```

### � **Development Mode** (Explicit flag required)
```bash
# Requires explicit -f flags for development
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Features:
# ✅ Local build with source code mounting
# ✅ Flask development server with hot-reload
# ✅ Debug mode enabled
# ✅ Instant code changes
```

> **💡 Note:** GHCR images support both `linux/amd64` and `linux/arm64` architectures. Production mode works on both Intel/AMD and Apple Silicon (M1/M2/M3) machines.

### 💡 **Quick Tips**

```bash
# Development workflow
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Production (simple, no flags)
docker compose up -d

# Update to latest production image
docker compose pull app
docker compose up -d

# View running containers
docker compose ps

# Stop all services
docker compose down
```

### ⚡ **Using Makefile (Shortcuts)**

For convenience, you can use Makefile commands:

```bash
make dev          # Development mode with hot-reload
make prod         # Production mode
make prod-pull    # Pull latest and start production
make down         # Stop all services
make logs         # View all logs
make logs-app     # View app logs only
make ps           # Show running containers
make help         # Show all available commands
```

### 📋 **Practical Usage Examples**

```bash
# Development workflow (local computer)
git clone https://github.com/ZekeriyaAY/track-finance.git
cd track-finance
make dev

# Production deployment (server)
make prod

# Or manually
docker compose pull app
docker compose up -d
```

### Database Management

**pgAdmin Setup:**
- Access: [http://localhost:5050](http://localhost:5050)
- Default Login: `admin@admin.com` / `admin123` (or your custom password)
- Database connection "Track Finance DB" is pre-configured
- Use your PostgreSQL password when prompted for database access

**Direct Database Access:**
```bash
# Connect directly to PostgreSQL container
docker compose exec db psql -U track_finance_user -d track_finance
```

--

## 🚀 Production Deployment

### GitHub Container Registry (GHCR) - Automated CI/CD

Every push to `master` branch automatically:
1. Builds production Docker image
2. Pushes to GitHub Container Registry
3. Image available at: `ghcr.io/zekeriyaay/track-finance:latest`

**Server Deployment:**
```bash
# Login to GHCR (one-time setup)
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Deploy latest version (clean command, no flags)
docker compose pull app
docker compose up -d
```

### 🐳 Portainer Deployment

Portainer automatically uses only `docker-compose.yml` (ignores override):

1. Copy `docker-compose.yml` content to Portainer Stack
2. Set environment variables through Portainer UI:
   - `POSTGRES_PASSWORD`, `SECRET_KEY`
   - `PGADMIN_DEFAULT_PASSWORD`, `GRAFANA_ADMIN_PASSWORD`
3. Deploy with one click

### Production Security Features

- ✅ **Security Headers:** XSS protection, clickjacking prevention, HTTPS enforcement
- ✅ **CSRF Protection:** All forms protected against cross-site attacks
- ✅ **Non-root Containers:** All services run as non-privileged users
- ✅ **Session Security:** Secure session management with proper timeouts
- ✅ **Database Security:** Connection pooling and prepared statements
- ✅ **Logging:** Structured logging with rotation for audit trails
- ✅ **Health Checks:** Built-in container health monitoring

---

## API Health Check

The application includes a health check endpoint for monitoring:

```bash
# Check application health
curl http://localhost:5001/health

# Response:
{
  "status": "healthy",
  "timestamp": "2025-10-03T10:00:00Z",
  "database": "connected"
}
```

---

## Project Structure

```
track-finance/
├── app.py                 # Flask application factory
├── config.py             # Environment configuration
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container definition
├── docker-compose.yml   # Service orchestration
├── models/              # Database models
├── routes/              # Application routes
├── templates/           # Jinja2 templates
├── static/             # CSS, JS, assets
├── utils/              # Helper utilities
└── migrations/         # Database migrations
```

## Stopping the Application

```bash
# Stop all services
docker compose down

# Stop and remove volumes (⚠️ deletes all data)
docker compose down -v

# View logs
docker compose logs -f app db
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and test thoroughly
4. Commit with clear messages: `git commit -m "Add new feature"`
5. Push to your fork: `git push origin feature/new-feature`
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Changelog

**v2.0.0** (October 2025)
- ✅ Removed multilingual support for simplified maintenance
- ✅ Production-ready security hardening
- ✅ Portainer integration support
- ✅ Environment variable optimization
- ✅ Docker security improvements
- ✅ CI/CD pipeline optimization