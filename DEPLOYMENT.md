# Deployment & Operations Guide

## 🚀 Quick Start

```bash
git clone <your-repo-url>
cd track-finance
make init
```

**Access Points:**
- **App**: http://localhost:5001
- **Grafana**: http://localhost:3000  
- **pgAdmin**: http://localhost:8080

## 🚀 Operations

### Make Commands
```bash
make up            # Start services
make down          # Stop services
make logs          # View logs
make restart       # Restart services
make migrate       # Run database migrations
make backup        # Backup database
make shell         # Access container shell
make clean         # Clean everything
```

### Grafana Commands
```bash
make show_grafana           # Show Grafana status
make grafana_logs          # View Grafana logs
make restart_grafana       # Restart Grafana
make setup_grafana_views   # Setup database views
```

## ⚙️ Configuration

Edit `.env.docker` for environment variables:
```bash
WEB_PORT=5001
GRAFANA_PORT=3000
PGADMIN_PORT=8080
POSTGRES_PASSWORD=secure-password
GRAFANA_ADMIN_PASSWORD=secure-password
```

## 🛠️ Troubleshooting

### Common Issues
```bash
# App won't start
make logs
make restart

# Database issues
make migrate
docker-compose exec db pg_isready

# Port conflicts
# Change WEB_PORT in .env.docker

# Reset everything
make clean
make init
```

### Performance
```bash
docker stats          # Check resource usage
make logs             # Check application logs
```

## 💾 Backup & Restore

```bash
make backup           # Database backup
```

## 🔒 Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Update database passwords  
- [ ] Configure firewall rules
- [ ] Setup regular backups
- [ ] Use HTTPS in production
