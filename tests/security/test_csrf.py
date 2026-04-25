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

    # ---- Settings endpoints ----

    def test_update_currency_requires_csrf(self, auth_client):
        """POST /settings/update-currency without CSRF token returns 400."""
        response = auth_client.post('/settings/update-currency', data={
            'currency_symbol': '$',
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
