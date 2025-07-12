# 💰 Finance Tracker

A modern Flask-based web application designed to help you easily track your personal income, expenses, and investments. It offers full control over your financial situation with features like categories, tags, and customizable investment types.

## 🚀 Quick Start with Docker

```bash
# Clone and start in one command
git clone <your-repo-url>
cd track-finance
make init
```

Visit: http://localhost:${WEB_PORT} (default: 5001)

For detailed deployment options, see [DEPLOYMENT.md](DEPLOYMENT.md)

## ✨ Features

- **Cash Flow Tracking:** Manage your income and expenses by date, category, and tags.
- **Investment Portfolio:** Track your various investments, such as stocks, currencies, and cryptocurrencies, along with their transaction history.
- **Flexible Categorization:** Organize your income and expenses hierarchically with main and sub-categories.
- **Tagging System:** Assign custom tags to your transactions for more detailed analysis.
- **Customizable Assets:** Define and manage your own investment types.
- **Easy Setup:** Get started immediately by creating a default data structure (categories, tags, investment types) with a single click.
- **Database Management:** Reset the entire database or generate sample data for testing purposes through the settings page.
- **Multi-language Support:** Internationalization (i18n) support with Flask-Babel for Turkish and English languages.
- **Modern UI:** A mobile-friendly and user-oriented interface developed with Tailwind CSS.
- **Docker Ready:** Production-ready Docker configuration with PostgreSQL and Nginx.

## 🛠️ Tech Stack

- **Backend:** Python, Flask, SQLAlchemy
- **Frontend:** HTML, Jinja2, Tailwind CSS, Font Awesome
- **Database:** PostgreSQL (Production), SQLite (Development)
- **Deployment:** Docker, Docker Compose, Gunicorn, Nginx
- **Database:** SQLite (default)
- **Database Migrations:** Flask-Migrate, Alembic
- **Internationalization:** Flask-Babel for multi-language support

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ZekeriyaAY/track-finance.git
    cd track-finance
    ```

2.  **Create and activate a virtual environment:**
    - **Windows:**
      ```bash
      python -m venv .venv
      .venv\Scripts\activate
      ```
    - **Linux/macOS:**
      ```bash
      python -m venv .venv
      source .venv/bin/activate
      ```

3.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create and migrate the database:**
    *The application will automatically create the `instance/finance.db` file on the first run.* To apply the migrations, run the following command:
    ```bash
    flask db upgrade
    ```

5.  **Run the application:**
    ```bash
    flask run
    ```

6.  Open your browser and navigate to `http://127.0.0.1:5000`.

## 📈 Usage

After starting the application for the first time, you can quickly set up the data structure:

1.  Navigate to **Settings** from the **Management** menu in the top-right corner.
2.  Use the following buttons to generate default data:
    - "Create Default Categories"
    - "Create Default Tags"
    - "Create Default Investment Types"
3.  You can also use the "Create Sample Data" button to see how the application works with populated data.

## 📂 Project Structure

```
track-finance/
├── app.py                  # Main Flask application file
├── models/                 # SQLAlchemy database models
│   ├── category.py
│   ├── tag.py
│   ├── cashflow.py
│   └── investment.py
├── routes/                 # Flask Blueprint routes
│   ├── category.py
│   ├── tag.py
│   ├── cashflow.py
│   ├── investment.py
│   ├── investment_type.py
│   └── settings.py
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── category/
│   ├── tag/
│   ├── cashflow/
│   ├── investment/
│   ├── investment_type/
│   └── settings/
├── static/                 # Static files (CSS, JS, etc.)
├── migrations/             # Database migration files
├── translations/           # Internationalization files
│   ├── en/                # English translations
│   └── tr/                # Turkish translations  
├── instance/               # Instance-specific files (e.g., database)
├── utils.py                # Helper functions (data creation, etc.)
├── messages.pot            # Translation template file
└── requirements.txt        # Python dependencies
```

## ⚙️ Configuration

### Environment Variables

The application supports configuration through environment variables. Copy the example file and customize:

```bash
# Copy example environment file  
cp .env.example .env

# Edit configuration
nano .env
```

**Key Variables:**
- `FLASK_ENV`: Application environment (development/production)
- `SECRET_KEY`: Flask secret key for security
- `DATABASE_URL`: Database connection string
- `WEB_PORT`: Web application port (default: 5001)
- `PGADMIN_PORT`: pgAdmin interface port (default: 8080)

See `.env.example` for full configuration options.

## 🤝 Contributing

Contributions are welcome! Please feel free to open a pull request or create an issue.

### General Contribution Steps

1.  Fork the project.
2.  Create a new feature branch (`git checkout -b feature/new-amazing-feature`).
3.  Commit your changes (`git commit -am 'Add some amazing feature'`).
4.  Push to the branch (`git push origin feature/new-amazing-feature`).
5.  Open a Pull Request.

### 🌍 Translation Contributions

The project supports internationalization (i18n) using Flask-Babel. Currently supported languages:
- **English (en)** - Default language
- **Turkish (tr)** - Turkish translation

#### Adding a New Language

1.  **Initialize a new language:**
    ```bash
    # Replace 'de' with your language code (e.g., 'fr', 'es', 'de')
    pybabel init -i messages.pot -d translations -l de
    ```

2.  **Translate the messages:**
    - Navigate to `translations/{language_code}/LC_MESSAGES/messages.po`
    - Translate the `msgstr` entries for each `msgid`

3.  **Compile the translations:**
    ```bash
    pybabel compile -d translations
    ```

4.  **Update the language selector:**
    - Add your language code to the `get_locale()` function in `app.py`
    - Update the language list: `if lang in ['en', 'tr', 'de']:`

#### Updating Existing Translations

1.  **Extract new translatable strings:**
    ```bash
    pybabel extract -F babel.cfg -k _l -o messages.pot .
    ```

2.  **Update existing translation files:**
    ```bash
    pybabel update -i messages.pot -d translations
    ```

3.  **Translate new/updated strings:**
    - Edit the respective `.po` files in `translations/{language_code}/LC_MESSAGES/`

4.  **Compile the translations:**
    ```bash
    pybabel compile -d translations
    ```

#### Babel Configuration

The project uses a `babel.cfg` file for configuration. If you need to add it, create it in the root directory:

```ini
[python: **.py]
[jinja2: **/templates/**.html]
extensions=jinja2.ext.autoescape,jinja2.ext.with_
```

#### Translation Workflow for Developers

When adding new translatable strings to the code:

1.  **In Python files:** Use `_('Your text here')` or `gettext('Your text here')`
2.  **In Jinja2 templates:** Use `{{ _('Your text here') }}`
3.  **Extract and update translations** using the commands above
4.  **Always compile translations** before testing

#### Translation Guidelines

- Keep translations contextually appropriate
- Maintain consistent terminology across the application
- Test the UI with different languages to ensure proper layout
- Consider text expansion/contraction in different languages

### 🛠️ Development Setup for Babel

If you're working on the internationalization features:

1.  **Install Babel CLI:**
    ```bash
    pip install Babel
    ```

2.  **Verify current translations:**
    ```bash
    # Check translation statistics
    pybabel compile -d translations --statistics
    ```

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
