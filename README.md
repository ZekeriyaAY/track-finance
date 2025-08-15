# 💰 Track Finance

Personal finance tracking web application with cash flow and investment management.

## Features

- Cash flow tracking (income/expenses)
- Investment portfolio management
- Excel bank statement import
- Multi-language support (EN/TR)
- Grafana analytics integration

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd track-finance
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Initialize database
flask db upgrade

# Run application
flask run --debug
```

**Access**: http://localhost:5000

## Database Management

### Model Changes & Migrations

When you modify database models, run these commands:

```bash
# Generate migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations to database
flask db upgrade

# Check migration status
flask db current

# Rollback to previous migration (if needed)
flask db downgrade
```

### Database Operations

```bash
# Reset database (⚠️ This will delete all data!)
flask db downgrade base
flask db upgrade

# Access database shell
flask shell
```

## Translation Management

When you add new `_('text')` strings to templates or code:

```bash
# Extract new translatable strings
pybabel extract -F babel.cfg -k _l -o messages.pot .

# Update existing translation files
pybabel update -i messages.pot -d translations

# Edit translation files manually
# translations/tr/LC_MESSAGES/messages.po
# translations/en/LC_MESSAGES/messages.po

# Compile translations after editing
pybabel compile -d translations
```

## Production

### Systemd Service (Recommended)

Create `/etc/systemd/system/track-finance.service`:

```ini
[Unit]
Description=Track Finance Gunicorn Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/track-finance
ExecStart=/home/ubuntu/track-finance/.venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable track-finance
sudo systemctl start track-finance
sudo systemctl status track-finance
```

### Manual Gunicorn

If you prefer to run Gunicorn manually:

```bash
# Using Gunicorn directly
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

© 2025 [Zekeriya AY](https://github.com/ZekeriyaAY)
