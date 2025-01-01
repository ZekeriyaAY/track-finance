# Track Finance

Track Finance is a personal finance management application that helps you monitor your expenses, track your income, and take control of your financial journey.

## Features

- **Transaction Management**: Track your income and expenses
- **Category Organization**: Organize transactions by categories
- **Brand Tracking**: Monitor spending by brands/vendors
- **Dashboard**: Get an overview of your financial status
- **User Management**: Secure user accounts with profile management
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Backend**: Python/Flask
- **Database**: SQLAlchemy (SQL)
- **Frontend**: Bootstrap 5
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Date/Time**: Flask-Moment
- **Icons**: Font Awesome

## Installation

1. Clone the repository

```shell
git clone https://github.com/ZekeriyaAY/track-finance.git
cd track-finance
```

2. Create and activate virtual environment

```shell
python3 -m venv env
source env/bin/activate
```

3. Install dependencies

```shell
pip install -r requirements.txt
```

4. Initialize the database

```shell
flask db upgrade
```

5. Run the application

```shell
flask run
```

The application will be available at `http://localhost:5000`

## Project Structure

```
track-finance/
├── app/                  # Application package
│   ├── errors/           # Error handling blueprint
│   ├── main/             # Main pages blueprint
│   ├── user/             # User management blueprint
│   ├── category/         # Category management blueprint
│   ├── brand/            # Brand management blueprint
│   ├── transaction/      # Transaction management blueprint
│   ├── dashboard/        # Dashboard blueprint
│   ├── static/           # Static files (CSS, JS)
│   │   └── style.css
│   └── templates/        # Jinja2 templates
│       └── partials/     # Reusable template parts
├── migrations/           # Database migrations
├── logs/                 # Application logs
├── .flaskenv             # Flask environment variables
├── config.py             # Application configuration
├── requirements.txt      # Python dependencies
└── main.py               # Application entry point
```

Each blueprint (`user`, `category`, etc.) follows a similar structure:

```
blueprint/
├── __init__.py          # Blueprint initialization
├── routes.py            # Route handlers
├── forms.py             # WTForms classes
└── templates/           # Blueprint-specific templates
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.

---

Version: 0.0.1  
Created by: [ZekeriyaAY](https://github.com/ZekeriyaAY)
