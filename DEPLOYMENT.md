# Deployment & Operations Guide

## 🚀 Quick Start

```bash
git clone <your-repo-url>
cd track-finance
cp .env.example .env
pip install -r requirements.txt
flask db upgrade
flask run
```

**Default Access Point:**
- **Web App**: http://localhost:5000

## ⚙️ Configuration

### Environment Variables (.env)

Copy from `.env.example` and configure:

```bash
cp .env.example .env
```

**Core Settings:**
- `FLASK_ENV`: `production` or `development`
- `FLASK_DEBUG`: `0` (production) or `1` (development)
- `SECRET_KEY`: Change from default for security
- `DATABASE_URL`: Your database connection string

**Database Configuration:**
The application uses SQLite database - no setup required:
```
DATABASE_URL=sqlite:///track_finance.db
```

## 🗄️ Database Setup

The application uses SQLite database which requires no additional setup.

```bash
# In .env file (default)
DATABASE_URL=sqlite:///track_finance.db
```

The database file will be automatically created when you run migrations:
```bash
flask db upgrade
```

The database file (`track_finance.db`) will be created in your project directory.

## 🚀 Running the Application

### Development Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run
```

### Production Mode
```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
flask run --host=0.0.0.0 --port=5000
```

### Using Gunicorn (Production Recommended)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## 🔄 Database Operations

```bash
# Run migrations
flask db upgrade

# Create new migration
flask db migrate -m "description"

# Database shell
flask shell
```

## 🛠️ Troubleshooting

### Application Won't Start
1. Check database connection in `.env`
2. Ensure database is running
3. Run migrations: `flask db upgrade`
4. Check Python dependencies: `pip install -r requirements.txt`

### Database Connection Issues
1. Verify database server is running
2. Check database credentials in `.env`
3. Test connection manually
4. Ensure database exists

### Import Errors
1. Activate virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Check Python path

## 🔒 Production Deployment

### Security Checklist
- [ ] **Change SECRET_KEY** in `.env`
- [ ] **Use strong database password**
- [ ] **Set FLASK_ENV=production**
- [ ] **Set FLASK_DEBUG=0**
- [ ] **Configure HTTPS** with reverse proxy
- [ ] **Set up firewall rules**

### Recommended Production Setup

1. **Use Gunicorn** as WSGI server
2. **Nginx** as reverse proxy
3. **Systemd** service for auto-start
4. **SSL/TLS** certificate
5. **Database backups**

### Example Systemd Service
Create `/etc/systemd/system/track-finance.service`:
```ini
[Unit]
Description=Track Finance Web App
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/track-finance
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Example Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring

### Log Files
- Application logs: Check Flask application logs
- Web server logs: Nginx/Apache access and error logs
- Database logs: SQLite operations are logged in application logs

### Health Checks
```bash
# Check if application is responding
curl http://localhost:5000/

# Database connection test
flask shell
>>> from app import db
>>> db.session.execute('SELECT 1')
```
