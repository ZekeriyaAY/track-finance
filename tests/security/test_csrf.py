"""Tests for CSRF protection on all POST endpoints.

Verifies that Flask-WTF CSRFProtect rejects requests without valid CSRF tokens.
All POST endpoints must return 400 when CSRF token is missing or invalid.
"""
import pytest
from io import BytesIO
from datetime import date, datetime
from models.category import Category
from models.tag import Tag
from models.cashflow import CashflowTransaction
from models.investment import InvestmentType, InvestmentTransaction
from models.bank_connection import BankConnection
from models import db as _db


@pytest.mark.security
class TestCSRFProtectionMissingToken:
    """All POST endpoints must reject requests without a CSRF token (HTTP 400)."""

    # ---- Auth endpoints ----

    def test_login_requires_csrf(self, client, admin_user):
        """POST /auth/login without CSRF token returns 400."""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'testpassword123',
        })
        assert response.status_code == 400

    def test_change_password_requires_csrf(self, auth_client):
        """POST /auth/change-password without CSRF token returns 400."""
        response = auth_client.post('/auth/change-password', data={
            'current_password': 'testpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456',
        })
        assert response.status_code == 400

    def test_change_username_requires_csrf(self, auth_client):
        """POST /auth/change-username without CSRF token returns 400."""
        response = auth_client.post('/auth/change-username', data={
            'new_username': 'newadmin',
            'password': 'testpassword123',
        })
        assert response.status_code == 400

    # ---- Cashflow endpoints ----

    def test_cashflow_add_requires_csrf(self, auth_client, sample_category):
        """POST /cashflow/add without CSRF token returns 400."""
        response = auth_client.post('/cashflow/add', data={
            'date': '2024-01-15',
            'amount': '100.00',
            'type': 'expense',
            'category_id': str(sample_category.id),
            'description': 'Test',
        })
        assert response.status_code == 400

    def test_cashflow_edit_requires_csrf(self, auth_client, sample_transaction):
        """POST /cashflow/edit/<id> without CSRF token returns 400."""
        response = auth_client.post(f'/cashflow/edit/{sample_transaction.id}', data={
            'date': '2024-01-15',
            'amount': '200.00',
            'type': 'expense',
            'category_id': str(sample_transaction.category_id),
            'description': 'Updated',
        })
        assert response.status_code == 400

    def test_cashflow_delete_requires_csrf(self, auth_client, sample_transaction):
        """POST /cashflow/delete/<id> without CSRF token returns 400."""
        response = auth_client.post(f'/cashflow/delete/{sample_transaction.id}')
        assert response.status_code == 400

    def test_cashflow_import_requires_csrf(self, auth_client):
        """POST /cashflow/import without CSRF token returns 400."""
        data = {
            'bank_code': 'yapikredi',
        }
        data['excel_file'] = (BytesIO(b'fake data'), 'test.xlsx')
        response = auth_client.post('/cashflow/import', data=data,
                                    content_type='multipart/form-data')
        assert response.status_code == 400

    def test_cashflow_sync_requires_csrf(self, auth_client):
        """POST /cashflow/sync without CSRF token returns 400."""
        response = auth_client.post('/cashflow/sync')
        assert response.status_code == 400

    def test_cashflow_bulk_edit_requires_csrf(self, auth_client, sample_transaction):
        """POST /cashflow/bulk-edit without CSRF token returns 400."""
        response = auth_client.post('/cashflow/bulk-edit', data={
            'transaction_ids[]': [str(sample_transaction.id)],
            'category_id': str(sample_transaction.category_id),
        })
        assert response.status_code == 400

    # ---- Category endpoints ----

    def test_category_add_requires_csrf(self, auth_client):
        """POST /categories/add without CSRF token returns 400."""
        response = auth_client.post('/categories/add', data={
            'name': 'New Category',
            'parent_id': '',
        })
        assert response.status_code == 400

    def test_category_edit_requires_csrf(self, auth_client, sample_category):
        """POST /categories/edit/<id> without CSRF token returns 400."""
        response = auth_client.post(f'/categories/edit/{sample_category.id}', data={
            'name': 'Renamed Category',
            'parent_id': '',
        })
        assert response.status_code == 400

    def test_category_delete_requires_csrf(self, auth_client, sample_category):
        """POST /categories/delete/<id> without CSRF token returns 400."""
        response = auth_client.post(f'/categories/delete/{sample_category.id}')
        assert response.status_code == 400

    # ---- Tag endpoints ----

    def test_tag_add_requires_csrf(self, auth_client):
        """POST /tags/add without CSRF token returns 400."""
        response = auth_client.post('/tags/add', data={
            'name': 'New Tag',
        })
        assert response.status_code == 400

    def test_tag_edit_requires_csrf(self, auth_client, sample_tag):
        """POST /tags/edit/<id> without CSRF token returns 400."""
        response = auth_client.post(f'/tags/edit/{sample_tag.id}', data={
            'name': 'Renamed Tag',
        })
        assert response.status_code == 400

    def test_tag_delete_requires_csrf(self, auth_client, sample_tag):
        """POST /tags/delete/<id> without CSRF token returns 400."""
        response = auth_client.post(f'/tags/delete/{sample_tag.id}')
        assert response.status_code == 400

    # ---- Investment endpoints ----

    def test_investment_add_requires_csrf(self, auth_client, sample_investment_type):
        """POST /investments/add without CSRF token returns 400."""
        response = auth_client.post('/investments/add', data={
            'investment_type_id': str(sample_investment_type.id),
            'transaction_date': '2024-01-15',
            'transaction_type': 'buy',
            'price': '100.00',
            'quantity': '5',
            'description': 'Test',
        })
        assert response.status_code == 400

    def test_investment_edit_requires_csrf(self, auth_client, sample_investment):
        """POST /investments/edit/<id> without CSRF token returns 400."""
        response = auth_client.post(f'/investments/edit/{sample_investment.id}', data={
            'investment_type_id': str(sample_investment.investment_type_id),
            'transaction_date': '2024-01-15',
            'transaction_type': 'buy',
            'price': '200.00',
            'quantity': '10',
            'description': 'Updated',
        })
        assert response.status_code == 400

    def test_investment_delete_requires_csrf(self, auth_client, sample_investment):
        """POST /investments/delete/<id> without CSRF token returns 400."""
        response = auth_client.post(f'/investments/delete/{sample_investment.id}')
        assert response.status_code == 400

    # ---- Investment Type endpoints ----

    def test_investment_type_add_requires_csrf(self, auth_client):
        """POST /investment-types/add without CSRF token returns 400."""
        response = auth_client.post('/investment-types/add', data={
            'name': 'Gold',
            'code': 'gold',
            'icon': 'fas fa-coins',
            'color': '#FFD700',
            'parent_id': '',
        })
        assert response.status_code == 400

    def test_investment_type_edit_requires_csrf(self, auth_client, sample_investment_type):
        """POST /investment-types/edit/<id> without CSRF token returns 400."""
        response = auth_client.post(f'/investment-types/edit/{sample_investment_type.id}', data={
            'name': 'Renamed Type',
            'code': 'renamed',
            'icon': 'fas fa-coins',
            'color': '#FFD700',
            'parent_id': '',
        })
        assert response.status_code == 400

    def test_investment_type_delete_requires_csrf(self, auth_client, sample_investment_type):
        """POST /investment-types/delete/<id> without CSRF token returns 400."""
        response = auth_client.post(f'/investment-types/delete/{sample_investment_type.id}')
        assert response.status_code == 400

    # ---- Settings endpoints ----

    def test_update_pgadmin_url_requires_csrf(self, auth_client):
        """POST /settings/update-pgadmin-url without CSRF token returns 400."""
        response = auth_client.post('/settings/update-pgadmin-url', data={
            'pgadmin_url': 'http://localhost:5050',
        })
        assert response.status_code == 400

    def test_create_dummy_data_requires_csrf(self, auth_client):
        """POST /settings/create-dummy-data without CSRF token returns 400."""
        response = auth_client.post('/settings/create-dummy-data')
        assert response.status_code == 400

    def test_create_default_categories_requires_csrf(self, auth_client):
        """POST /settings/create-default-categories without CSRF token returns 400."""
        response = auth_client.post('/settings/create-default-categories')
        assert response.status_code == 400

    def test_create_default_tags_requires_csrf(self, auth_client):
        """POST /settings/create-default-tags without CSRF token returns 400."""
        response = auth_client.post('/settings/create-default-tags')
        assert response.status_code == 400

    def test_create_default_investment_types_requires_csrf(self, auth_client):
        """POST /settings/create-default-investment-types without CSRF token returns 400."""
        response = auth_client.post('/settings/create-default-investment-types')
        assert response.status_code == 400

    def test_bank_connection_add_requires_csrf(self, auth_client):
        """POST /settings/bank-connections/add without CSRF token returns 400."""
        response = auth_client.post('/settings/bank-connections/add', data={
            'bank_code': 'yapikredi',
            'client_id': 'test_id',
            'client_secret': 'test_secret',
        })
        assert response.status_code == 400

    def test_bank_connection_delete_requires_csrf(self, app, auth_client, db):
        """POST /settings/bank-connections/delete/<id> without CSRF token returns 400."""
        with app.app_context():
            conn = BankConnection(
                bank_code='yapikredi',
                bank_name='Yapi Kredi',
            )
            conn.set_client_id('test')
            conn.set_client_secret('test')
            db.session.add(conn)
            db.session.commit()
            conn_id = conn.id

        response = auth_client.post(f'/settings/bank-connections/delete/{conn_id}')
        assert response.status_code == 400

    def test_bank_connection_toggle_requires_csrf(self, app, auth_client, db):
        """POST /settings/bank-connections/toggle/<id> without CSRF token returns 400."""
        with app.app_context():
            conn = BankConnection(
                bank_code='yapikredi',
                bank_name='Yapi Kredi',
            )
            conn.set_client_id('test')
            conn.set_client_secret('test')
            db.session.add(conn)
            db.session.commit()
            conn_id = conn.id

        response = auth_client.post(f'/settings/bank-connections/toggle/{conn_id}')
        assert response.status_code == 400

    def test_bank_connection_test_requires_csrf(self, app, auth_client, db):
        """POST /settings/bank-connections/test/<id> without CSRF token returns 400."""
        with app.app_context():
            conn = BankConnection(
                bank_code='yapikredi',
                bank_name='Yapi Kredi',
            )
            conn.set_client_id('test')
            conn.set_client_secret('test')
            db.session.add(conn)
            db.session.commit()
            conn_id = conn.id

        response = auth_client.post(f'/settings/bank-connections/test/{conn_id}')
        assert response.status_code == 400

    def test_reset_database_requires_csrf(self, auth_client):
        """POST /settings/reset-database without CSRF token returns 400."""
        response = auth_client.post('/settings/reset-database')
        assert response.status_code == 400


@pytest.mark.security
class TestCSRFProtectionInvalidToken:
    """POST endpoints must reject requests with an invalid CSRF token."""

    def test_login_rejects_invalid_csrf(self, client, admin_user):
        """POST /auth/login with invalid CSRF token returns 400."""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'testpassword123',
            'csrf_token': 'totally-invalid-token-value',
        })
        assert response.status_code == 400

    def test_category_add_rejects_invalid_csrf(self, auth_client):
        """POST /categories/add with invalid CSRF token returns 400."""
        response = auth_client.post('/categories/add', data={
            'name': 'Category',
            'parent_id': '',
            'csrf_token': 'not-a-real-token',
        })
        assert response.status_code == 400

    def test_tag_add_rejects_invalid_csrf(self, auth_client):
        """POST /tags/add with invalid CSRF token returns 400."""
        response = auth_client.post('/tags/add', data={
            'name': 'Tag',
            'csrf_token': 'forged-csrf-token',
        })
        assert response.status_code == 400

    def test_cashflow_add_rejects_invalid_csrf(self, auth_client, sample_category):
        """POST /cashflow/add with invalid CSRF token returns 400."""
        response = auth_client.post('/cashflow/add', data={
            'date': '2024-01-15',
            'amount': '100.00',
            'type': 'expense',
            'category_id': str(sample_category.id),
            'description': 'Test',
            'csrf_token': 'wrong-token-123',
        })
        assert response.status_code == 400

    def test_investment_add_rejects_invalid_csrf(self, auth_client, sample_investment_type):
        """POST /investments/add with invalid CSRF token returns 400."""
        response = auth_client.post('/investments/add', data={
            'investment_type_id': str(sample_investment_type.id),
            'transaction_date': '2024-01-15',
            'transaction_type': 'buy',
            'price': '100.00',
            'quantity': '5',
            'description': 'Test',
            'csrf_token': 'bad-csrf-value',
        })
        assert response.status_code == 400

    def test_settings_update_pgadmin_rejects_invalid_csrf(self, auth_client):
        """POST /settings/update-pgadmin-url with invalid CSRF token returns 400."""
        response = auth_client.post('/settings/update-pgadmin-url', data={
            'pgadmin_url': 'http://localhost:5050',
            'csrf_token': 'bogus-token',
        })
        assert response.status_code == 400

    def test_reset_database_rejects_invalid_csrf(self, auth_client):
        """POST /settings/reset-database with invalid CSRF token returns 400."""
        response = auth_client.post('/settings/reset-database', data={
            'csrf_token': 'fake-token-value',
        })
        assert response.status_code == 400

    def test_change_password_rejects_invalid_csrf(self, auth_client):
        """POST /auth/change-password with invalid CSRF token returns 400."""
        response = auth_client.post('/auth/change-password', data={
            'current_password': 'testpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456',
            'csrf_token': 'invalid-token',
        })
        assert response.status_code == 400
