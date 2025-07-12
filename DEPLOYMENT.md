# Production Deployment Guide

## 🐳 Simplified Docker Production Deployment

This project uses a minimal Docker setup with just Flask and PostgreSQL for production environments.

### Architecture
- **Web Service**: Flask app running on Python 3.11 with development server
- **Database**: PostgreSQL 15 with persistent storage
- **No Nginx**: Direct connection to Flask (simplified for single-domain deployment)
- **No Gunicorn**: Using Flask's built-in server for simplicity

### Prerequisites
- Docker & Docker Compose installed
- Git

### Quick Start (First Time Setup)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd track-finance

# 2. Initialize everything with one command
make init
```

That's it! Your Finance Tracker will be running at http://localhost:${WEB_PORT} (default: 5001)

### Manual Setup (Alternative)

```bash
# 1. Clone and setup
git clone <your-repo-url>
cd track-finance

# 2. Copy environment file (optional)
cp .env.docker .env
# Edit .env with your production values if needed

# 3. Build and start services
docker-compose build
docker-compose up -d

# 4. Run initial database migration
docker-compose exec web flask db upgrade

# 5. Create default data (optional)
docker-compose exec web flask shell
>>> from utils import create_dummy_data
>>> create_dummy_data()
>>> exit()
```

## 🚀 Daily Operations

### Using Make Commands (Recommended)
```bash
make help          # Show all available commands
make up            # Start services
make down          # Stop services
make logs          # View logs
make restart       # Restart services
make migrate       # Run database migrations
make backup        # Backup database
make shell         # Access container shell
make clean         # Clean everything (use with caution)
```

### Using Docker Compose Directly
```bash
docker-compose up -d              # Start services
docker-compose down               # Stop services
docker-compose logs -f            # View logs
docker-compose exec web bash     # Access web container
docker-compose exec db psql -U ${POSTGRES_USER} ${POSTGRES_DB}  # Access database
```

## 🔧 Configuration

### Environment Variables
The application uses environment variables for configuration. Copy the example file and customize:

```bash
# Copy example environment file
cp .env.example .env.docker

# Edit environment variables
nano .env.docker
```

### Environment Variables

All configuration is managed through environment variables. Here's a quick reference:

**Application Configuration:**
- `FLASK_ENV`: Application environment (development/production)
- `SECRET_KEY`: Flask security secret (change for production!)
- `WEB_PORT`: Web application port (default: 5001)

**Database Configuration:**
- `POSTGRES_DB`: Database name (default: finance_db)
- `POSTGRES_USER`: Database username (default: finance_user)  
- `POSTGRES_PASSWORD`: Database password (default: finance_pass)
- `DATABASE_URL`: Full database connection string

**pgAdmin Configuration:**
- `PGADMIN_PORT`: pgAdmin web interface port (default: 8080)
- `PGADMIN_DEFAULT_EMAIL`: pgAdmin login email
- `PGADMIN_DEFAULT_PASSWORD`: pgAdmin login password

**Health Check Configuration:**
- `HEALTH_CHECK_INTERVAL`: Web app health check frequency (default: 30s)
- `HEALTH_CHECK_TIMEOUT`: Health check timeout (default: 10s)
- `HEALTH_CHECK_RETRIES`: Health check retry attempts (default: 3)
- `DB_HEALTH_CHECK_*`: Database-specific health check settings

**Security & Internationalization:**
- `CSRF_ENABLED`: Enable CSRF protection (default: True)
- `LANGUAGES`: Supported languages (default: en,tr)

For complete list with detailed descriptions, see `.env.example` file.

### Port Configuration
- **Web App**: Configured via `WEB_PORT` (default: 5001)
- **pgAdmin**: Configured via `PGADMIN_PORT` (default: 8080)  
- **Database**: Internal PostgreSQL port 5432

### Security Notes
- Change default passwords in production
- Use strong `SECRET_KEY` values
- Consider using Docker secrets for sensitive data
- The `.env.docker` file is excluded from git for security

## Home Server Development Workflow

### Initial Setup on Your Home Server

1. **First time setup on your server:**
```bash
# SSH into your home server
ssh user@your-home-server-ip

# Clone the repository
git clone https://github.com/ZekeriyaAY/track-finance.git
cd track-finance

# Initialize the application
make init

# Your app is now running at http://your-server-ip:${WEB_PORT}
# Default port is 5001, but configurable via .env.docker
```

### Development & Update Workflow

When you make changes to your code:

**Recommended: Use the built-in update command**
```bash
# 1. On your local machine - commit and push changes
git add .
git commit -m "Your changes description"
git push origin main

# 2. On your home server - one command update
ssh user@your-home-server-ip
cd track-finance
make update  # This pulls changes, rebuilds, and restarts containers
```

**Alternative: Manual update**
```bash
# On your home server
git pull origin main
make restart
```

### Network Access Options

- **Local network**: `http://192.168.1.x:${WEB_PORT}` (default port 5001)
- **Internet access**: Port forward `${WEB_PORT}` or use reverse proxy
- **Custom domain**: Setup DNS + reverse proxy for HTTPS

### Tips for Home Server Usage

1. **SSH Keys**: Use SSH keys for passwordless access
2. **Static IP**: Configure static IP for your server  
3. **Firewall**: Open only ports 22 (SSH) and 5000 (app)
4. **Backup Strategy**: Use `make backup` regularly
5. **Monitoring**: Use `docker stats` and `make logs`

## 🔒 Security Best Practices

### Production Security Checklist
- [ ] SECRET_KEY changed (default value not used)
- [ ] Database passwords strengthened (16+ characters)
- [ ] HTTPS usage (SSL certificates)
- [ ] Firewall rules configured (only necessary ports)
- [ ] Regular backup strategy implemented
- [ ] Environment variables (.env) stored securely

### Quick Security Setup
```bash
# 1. Generate strong secret key
openssl rand -hex 32

# 2. Update in .env file
nano .env
# SECRET_KEY=generated-key-from-above

# 3. Update database passwords
# Change POSTGRES_PASSWORD in both docker-compose.yml and .env
```

##  Monitoring & Maintenance

### Health Checks
```bash
# Check container status
docker-compose ps

# Check application health
curl http://localhost:${WEB_PORT}/

# View resource usage
docker stats
```

### Logs
```bash
make logs                           # All services
docker-compose logs web            # Web application only
docker-compose logs db             # Database only
```

### Updates
```bash
# Update application
git pull
docker-compose build
docker-compose up -d
make migrate  # If database changes

# Update base images
docker-compose pull
docker-compose up -d
```

## 💾 Backup & Restore

### Database Backup
```bash
make backup  # Creates timestamped SQL dump
```

### Database Restore
```bash
# Restore from backup file
docker-compose exec db psql -U ${POSTGRES_USER} ${POSTGRES_DB} < backup_YYYYMMDD_HHMMSS.sql
```

### Full System Backup
```bash
# Backup PostgreSQL volume
docker run --rm -v track-finance_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

## 🔧 Troubleshooting

### Container Won't Start
```bash
docker-compose logs web  # Check web container logs
docker-compose logs db   # Check database logs
```

### Database Connection Issues
```bash
# Check database container
docker-compose exec db pg_isready -U ${POSTGRES_USER}

# Reset database
docker-compose down
docker volume rm track-finance_postgres_data
make init
```

### Port Conflicts
```bash
# Change ports in .env.docker
WEB_PORT=8080     # Use port 8080 instead of 5001
PGADMIN_PORT=9090 # Change pgAdmin port if needed
```

### Performance Issues
```bash
# Check resource usage
docker stats
```

## 📞 Support

### Quick Fixes
1. **App not loading**: `make restart`
2. **Database issues**: `make migrate`
3. **Performance**: `docker stats` to check resource usage

### Debug Mode
```bash
# Run with debug logs
FLASK_ENV=development docker-compose up

# Access container shell
make shell
```

## 🔧 Database Management

### pgAdmin Web Interface
The application includes pgAdmin, a comprehensive web-based PostgreSQL administration tool:

1. **Access pgAdmin**: Navigate to http://localhost:${PGADMIN_PORT}
2. **Login credentials** (configurable in .env.docker):
   - Email: `${PGADMIN_DEFAULT_EMAIL}`
   - Password: `${PGADMIN_DEFAULT_PASSWORD}`

3. **Add Database Server** (first time setup):
   - Right-click "Servers" → "Create" → "Server"
   - **General Tab**:
     - Name: `Finance Tracker DB`
   - **Connection Tab**:
     - Host: `db`
     - Port: `5432`
     - Username: `${POSTGRES_USER}`
     - Password: `${POSTGRES_PASSWORD}`
     - Database: `${POSTGRES_DB}`

4. **Features available**:
   - Advanced query editor with syntax highlighting
   - Visual database schema browser
   - Data import/export tools
   - User and permission management
   - Performance monitoring and statistics
   - Backup and restore operations
   - Visual query planner

### Quick Access
```bash
make dbadmin    # Opens pgAdmin in browser with connection info
```

### Direct Database Access
```bash
# Access PostgreSQL directly
docker-compose exec db psql -U ${POSTGRES_USER} ${POSTGRES_DB}

# View database logs
docker-compose logs db

# Create database backup
make backup
```
