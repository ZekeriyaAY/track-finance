# Deployment & Operations Guide

## 🚀 Quick Start

```bash
git clone <your-repo-url>
cd track-finance
make setup
```

**Access Points:**
- **App**: http://localhost:5000
- **Grafana**: http://localhost:3000  
- **pgAdmin**: http://localhost:8080

## 🚀 Operations

### Main Commands
```bash
make setup         # First time setup (copies .env.example to .env)
make up            # Start services (production mode)
make debug         # Start with debug mode enabled
make down          # Stop services
make logs          # View logs
make restart       # Restart services
make backup        # Backup database
```

### Database Commands
```bash
make migrate       # Run database migrations
make shell         # Access web container shell
```

## ⚙️ Configuration

All configuration is done through the `.env` file. See `.env.example` for all available options with detailed comments.

For debug mode, set `FLASK_ENV=development` and `FLASK_DEBUG=1`.

## 🛠️ Troubleshooting

### Common Issues
```bash
# App won't start
make logs
make restart

# Database connection issues
make migrate
docker-compose exec db pg_isready

# Port conflicts - edit .env file:
WEB_PORT=5001
PGADMIN_PORT=8081

# Complete reset
make down
docker-compose down -v
make setup
```

### Debug Mode
```bash
# Temporary debug mode
make debug

# Permanent debug mode - edit .env:
FLASK_ENV=development
FLASK_DEBUG=1
```

## 🔒 Security Checklist

- [ ] Change default SECRET_KEY in .env
- [ ] Update all passwords in .env
- [ ] Use strong GRAFANA_ADMIN_PASSWORD
- [ ] Configure firewall rules for production
- [ ] Setup regular backups with `make backup`
- [ ] Use HTTPS in production deployment
