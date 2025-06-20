# 💰 Finance Tracker

A modern Flask-based web application designed to help you easily track your personal income, expenses, and investments. It offers full control over your financial situation with features like categories, tags, and customizable investment types.

## ✨ Features

- **Cash Flow Tracking:** Manage your income and expenses by date, category, and tags.
- **Investment Portfolio:** Track your various investments, such as stocks, currencies, and cryptocurrencies, along with their transaction history.
- **Flexible Categorization:** Organize your income and expenses hierarchically with main and sub-categories.
- **Tagging System:** Assign custom tags to your transactions for more detailed analysis.
- **Customizable Assets:** Define and manage your own investment types.
- **Easy Setup:** Get started immediately by creating a default data structure (categories, tags, investment types) with a single click.
- **Database Management:** Reset the entire database or generate sample data for testing purposes through the settings page.
- **Modern UI:** A mobile-friendly and user-oriented interface developed with Tailwind CSS.

## 🛠️ Tech Stack

- **Backend:** Python, Flask, SQLAlchemy
- **Frontend:** HTML, Jinja2, Tailwind CSS, Font Awesome
- **Database:** SQLite (default)
- **Database Migrations:** Flask-Migrate, Alembic

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
├── instance/               # Instance-specific files (e.g., database)
├── utils.py                # Helper functions (data creation, etc.)
└── requirements.txt        # Python dependencies
```

## 🤝 Contributing

Contributions are welcome! Please feel free to open a pull request or create an issue.

1.  Fork the project.
2.  Create a new feature branch (`git checkout -b feature/new-amazing-feature`).
3.  Commit your changes (`git commit -am 'Add some amazing feature'`).
4.  Push to the branch (`git push origin feature/new-amazing-feature`).
5.  Open a Pull Request.
