"""Shared test fixtures for Track Finance test suite."""
import os
import re
import pytest
from datetime import date, datetime

# Set env BEFORE any app imports so module-level create_app() uses TestingConfig
os.environ['FLASK_ENV'] = 'testing'

from models import db as _db
from models.user import User
from models.category import Category
from models.tag import Tag
from models.cashflow import CashflowTransaction
from models.investment import InvestmentType, InvestmentTransaction
from models.settings import Settings
from models.bank_connection import BankConnection


@pytest.fixture(scope='session')
def app():
    """Return the module-level Flask app (already created with TestingConfig
    because FLASK_ENV was set to 'testing' before the import)."""
    from app import app as flask_app

    with flask_app.app_context():
        _db.create_all()

    yield flask_app

    with flask_app.app_context():
        _db.drop_all()


@pytest.fixture(autouse=True)
def db(app):
    """Provide a clean database for every test.

    Pushes an app context, creates all tables, yields the db instance,
    then rolls back and drops all tables so tests are fully isolated.
    """
    with app.app_context():
        _db.create_all()
        # Keep attribute values on objects after commit so fixtures remain usable
        _db.session.expire_on_commit = False
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture()
def admin_user(db):
    """Create and return an admin user."""
    user = User(username='admin')
    user.set_password('testpassword123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def auth_client(client, admin_user):
    """Create an authenticated test client."""
    csrf = _get_csrf_token(client)
    client.post('/auth/login', data={
        'username': 'admin',
        'password': 'testpassword123',
        'csrf_token': csrf,
    }, follow_redirects=True)
    return client


def _get_csrf_token(client):
    """Extract CSRF token from the login page."""
    response = client.get('/auth/login')
    data = response.data.decode()
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', data)
    if match:
        return match.group(1)
    match = re.search(r'value="([^"]+)"[^>]*name="csrf_token"', data)
    if match:
        return match.group(1)
    return ''


def get_csrf_token(client, url='/auth/login'):
    """Extract CSRF token from any page. Utility for tests."""
    response = client.get(url)
    data = response.data.decode()
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', data)
    if match:
        return match.group(1)
    match = re.search(r'value="([^"]+)"[^>]*name="csrf_token"', data)
    if match:
        return match.group(1)
    return ''


@pytest.fixture()
def sample_category(db):
    """Create a sample parent category."""
    cat = Category(name='Test Category')
    db.session.add(cat)
    db.session.commit()
    return cat


@pytest.fixture()
def sample_subcategory(db, sample_category):
    """Create a sample subcategory."""
    sub = Category(name='Test Subcategory', parent_id=sample_category.id)
    db.session.add(sub)
    db.session.commit()
    return sub


@pytest.fixture()
def sample_tag(db):
    """Create a sample tag."""
    tag = Tag(name='Test Tag')
    db.session.add(tag)
    db.session.commit()
    return tag


@pytest.fixture()
def sample_transaction(db, sample_category, sample_tag):
    """Create a sample cashflow transaction."""
    txn = CashflowTransaction(
        date=date(2024, 1, 15),
        type='expense',
        amount=100.50,
        description='Test transaction',
        category_id=sample_category.id,
        source='manual',
    )
    txn.tags = [sample_tag]
    db.session.add(txn)
    db.session.commit()
    return txn


@pytest.fixture()
def sample_investment_type(db):
    """Create a sample investment type."""
    inv_type = InvestmentType(
        name='Test Stock',
        code='test_stock',
        icon='fas fa-chart-line',
        color='#3B82F6',
    )
    db.session.add(inv_type)
    db.session.commit()
    return inv_type


@pytest.fixture()
def sample_investment(db, sample_investment_type):
    """Create a sample investment transaction."""
    inv = InvestmentTransaction(
        investment_type_id=sample_investment_type.id,
        transaction_date=datetime(2024, 1, 15),
        transaction_type='buy',
        price=150.0,
        quantity=10.0,
        description='Test investment',
    )
    db.session.add(inv)
    db.session.commit()
    return inv
