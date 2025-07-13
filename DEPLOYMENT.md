# Deployment & Operations Guide

## 🚀 Quick Start

```bash
git clone <your-repo-url>
cd track-finance
make setup
```

**Default Access Points:**
- **Web App**: http://localhost:5000
- **Grafana Analytics**: http://localhost:3000  
- **pgAdmin Database**: http://localhost:8080

> **Note**: Ports can be customized in `.env` file

## 🚀 Operations & Commands

### Essential Commands
```bash
make setup         # First time setup (copies .env.example to .env)
make up            # Start all services (production mode)
make dev           # Start with debug mode enabled
make down          # Stop all services
make restart       # Restart all services
make logs          # View logs from all services
make status        # Show service status and health checks
```

### Database Operations
```bash
make migrate       # Run database migrations
make backup        # Create database backup
make init-db       # Initialize database (first time only)
make shell         # Access web container shell
```

### Maintenance Commands
```bash
make clean         # Remove containers, networks, volumes
make update        # Update containers with latest config
make pgadmin       # Open pgAdmin in browser
```

## ⚙️ Configuration

### Environment Variables (.env)

All configuration is managed through the `.env` file. Copy from `.env.example`:

**Core Settings:**
- `FLASK_ENV`: `production` or `development`
- `FLASK_DEBUG`: `0` (production) or `1` (development)
- `SECRET_KEY`: Change from default for security

**Database:**
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `DATABASE_URL`: Auto-generated from above

**Service Ports:**
- `WEB_PORT=5000`: Web application port
- `GRAFANA_PORT=3000`: Grafana analytics port  
- `PGADMIN_PORT=8080`: Database admin port

**Service Credentials:**
- `PGADMIN_DEFAULT_EMAIL`, `PGADMIN_DEFAULT_PASSWORD`
- `GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD`

### Debug Mode Configuration

**Temporary debug mode:**
```bash
make dev  # Enables debug for this session
```

**Permanent debug mode** (edit `.env`):
```bash
FLASK_ENV=development
FLASK_DEBUG=1
```

## 🛠️ Troubleshooting & Issues

### System Compatibility Issues

#### Ubuntu/Python 3.12 `distutils` Error

**Problem:** `ModuleNotFoundError: No module named 'distutils'`

This occurs with older docker-compose versions on Python 3.12+ systems.

**Solutions (in order of preference):**

```bash
# Option 1: Install missing package (quickest)
sudo apt update
sudo apt install python3-distutils

# Option 2: Upgrade to Docker Compose v2 (recommended)
sudo apt remove docker-compose
sudo apt install docker-compose-plugin
docker compose version  # Should show v2.x.x

# Option 3: Install via pip (alternative)
sudo apt remove docker-compose  
pip3 install docker-compose

# After any fix, retry setup:
make setup
```

### Common Operational Issues

#### Application Won't Start
```bash
# Check service status
make status

# View detailed logs
make logs

# Restart services
make restart

# Complete reset if needed
make down
make clean
make setup
```

#### Database Connection Issues
```bash
# Run migrations
make migrate

# Check database readiness
docker compose exec db pg_isready -U postgres

# Reset database completely
make down
docker volume rm track-finance_postgres_data
make setup
```

#### Port Conflicts
Edit `.env` file to change default ports:
```bash
WEB_PORT=5001        # Instead of 5000
GRAFANA_PORT=3001    # Instead of 3000  
PGADMIN_PORT=8081    # Instead of 8080
```

#### Permission Errors (Linux)
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again, or:
newgrp docker

# Verify docker access
docker ps
```

## 🔒 Security & Production Checklist

### Pre-Production Security
- [ ] **Change SECRET_KEY** in `.env` from default value
- [ ] **Update all passwords** in `.env` with strong passwords
- [ ] **Set strong GRAFANA_ADMIN_PASSWORD**
- [ ] **Use FLASK_ENV=production** and **FLASK_DEBUG=0**

### Production Deployment
- [ ] **Configure firewall rules** (ports 5000, 3000, 8080)
- [ ] **Setup HTTPS/SSL** with reverse proxy (nginx/traefik)
- [ ] **Configure backup schedule** with `make backup`
- [ ] **Monitor logs** regularly with `make logs`
- [ ] **Setup external database** for high availability
- [ ] **Configure volume mounts** for persistent data

### Monitoring & Maintenance
```bash
# Regular health checks
make status

# Backup schedule (add to crontab)
0 2 * * * cd /path/to/track-finance && make backup

# Update containers monthly
make update
```
