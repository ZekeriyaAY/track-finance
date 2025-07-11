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

That's it! Your Finance Tracker will be running at http://localhost:5001

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
docker-compose exec db psql -U finance_user finance_db  # Access database
```

## 🔧 Configuration

### Environment Variables
Edit `.env` file for custom configuration:

```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=postgresql://finance_user:finance_pass@db:5432/finance_db
```

### Database Configuration
- **Default**: PostgreSQL in Docker container
- **External DB**: Set `DATABASE_URL` to external PostgreSQL instance
- **Backup**: Use `make backup` for database dumps

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

# Your app is now running at http://your-server-ip:5001
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

- **Local network**: `http://192.168.1.x:5001`
- **Internet access**: Port forward 5001 or use reverse proxy
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
curl http://localhost:5001/

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
docker-compose exec db psql -U finance_user finance_db < backup_YYYYMMDD_HHMMSS.sql
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
docker-compose exec db pg_isready -U finance_user

# Reset database
docker-compose down
docker volume rm track-finance_postgres_data
make init
```

### Port Conflicts
```bash
# Change ports in docker-compose.yml
ports:
  - "8080:5000"  # Use port 8080 instead of 5000
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
