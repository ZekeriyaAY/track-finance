"""Integration tests for cashflow routes (/cashflow)."""
import pytest
from datetime import date, datetime
from tests.conftest import get_csrf_token
from models.cashflow import CashflowTransaction
from models.category import Category
from models.tag import Tag


pytestmark = pytest.mark.integration


class TestDashboardRoute:
    """Tests for GET /cashflow/dashboard."""

    def test_dashboard_renders(self, auth_client):
        """GET /cashflow/dashboard returns 200 with dashboard content."""
        response = auth_client.get('/cashflow/dashboard')
        assert response.status_code == 200

    def test_dashboard_with_date_filters(self, auth_client):
        """GET /cashflow/dashboard with date filter params returns 200."""
        response = auth_client.get(
            '/cashflow/dashboard?date_from=2024-01-01&date_to=2024-12-31'
        )
        assert response.status_code == 200

    def test_dashboard_with_invalid_date_filters(self, auth_client):
        """GET /cashflow/dashboard with invalid dates uses defaults gracefully."""
        response = auth_client.get(
            '/cashflow/dashboard?date_from=invalid&date_to=also-invalid'
        )
        assert response.status_code == 200

    def test_dashboard_shows_kpi_data(self, auth_client, sample_transaction):
        """Dashboard renders KPI values when transactions exist."""
        response = auth_client.get(
            '/cashflow/dashboard?date_from=2024-01-01&date_to=2024-12-31'
        )
        assert response.status_code == 200
        # The page should contain numeric data (the transaction amount)
        assert b'100' in response.data

    def test_dashboard_requires_auth(self, client, admin_user):
        """Dashboard redirects to login when not authenticated."""
        response = client.get('/cashflow/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers.get('Location', '')


class TestCashflowIndexRoute:
    """Tests for GET /cashflow/."""

    def test_index_renders(self, auth_client):
        """GET /cashflow/ returns 200 with transaction list."""
        response = auth_client.get('/cashflow/')
        assert response.status_code == 200

    def test_index_shows_transactions(self, auth_client, sample_transaction):
        """GET /cashflow/ shows existing transactions."""
        response = auth_client.get('/cashflow/')
        assert response.status_code == 200
        assert b'Test transaction' in response.data

    def test_index_filter_by_category(self, auth_client, sample_transaction, sample_category):
        """GET /cashflow/ filtered by category_id shows matching transactions."""
        response = auth_client.get(f'/cashflow/?category_id={sample_category.id}')
        assert response.status_code == 200
        assert b'Test transaction' in response.data

    def test_index_filter_by_tag(self, auth_client, sample_transaction, sample_tag):
        """GET /cashflow/ filtered by tag_id shows matching transactions."""
        response = auth_client.get(f'/cashflow/?tag_id={sample_tag.id}')
        assert response.status_code == 200
        assert b'Test transaction' in response.data

    def test_index_filter_by_type_expense(self, auth_client, sample_transaction):
        """GET /cashflow/ filtered by type=expense shows expense transactions."""
        response = auth_client.get('/cashflow/?type=expense')
        assert response.status_code == 200
        assert b'Test transaction' in response.data

    def test_index_filter_by_type_income(self, auth_client, sample_transaction):
        """GET /cashflow/ filtered by type=income excludes expense transactions."""
        response = auth_client.get('/cashflow/?type=income')
        assert response.status_code == 200
        # The sample_transaction is an expense, so it should not appear
        assert b'Test transaction' not in response.data

    def test_index_filter_by_date_range(self, auth_client, sample_transaction):
        """GET /cashflow/ filtered by date range returns matching transactions."""
        response = auth_client.get(
            '/cashflow/?date_from=2024-01-01&date_to=2024-01-31'
        )
        assert response.status_code == 200
        assert b'Test transaction' in response.data

    def test_index_filter_by_date_range_excludes(self, auth_client, sample_transaction):
        """GET /cashflow/ filtered by out-of-range dates excludes transactions."""
        response = auth_client.get(
            '/cashflow/?date_from=2025-01-01&date_to=2025-12-31'
        )
        assert response.status_code == 200
        assert b'Test transaction' not in response.data

    def test_index_filter_by_search(self, auth_client, sample_transaction):
        """GET /cashflow/ with search term filters transactions by description."""
        response = auth_client.get('/cashflow/?search=Test')
        assert response.status_code == 200
        assert b'Test transaction' in response.data

    def test_index_filter_by_search_no_match(self, auth_client, sample_transaction):
        """GET /cashflow/ with non-matching search returns no results."""
        response = auth_client.get('/cashflow/?search=nonexistentterm')
        assert response.status_code == 200
        assert b'Test transaction' not in response.data

    def test_index_filter_invalid_type_ignored(self, auth_client, sample_transaction):
        """GET /cashflow/ with invalid type filter is ignored (shows all)."""
        response = auth_client.get('/cashflow/?type=invalid')
        assert response.status_code == 200
        # Invalid type is not in ['income', 'expense'], so no filter applied
        assert b'Test transaction' in response.data

    def test_index_filter_by_parent_category_includes_subcategories(
        self, auth_client, app, db, sample_category, sample_subcategory
    ):
        """Filtering by parent category also includes subcategory transactions."""
        with app.app_context():
            txn = CashflowTransaction(
                date=date(2024, 2, 1),
                type='expense',
                amount=50.0,
                description='Subcategory transaction',
                category_id=sample_subcategory.id,
                source='manual',
            )
            db.session.add(txn)
            db.session.commit()

        response = auth_client.get(f'/cashflow/?category_id={sample_category.id}')
        assert response.status_code == 200
        assert b'Subcategory transaction' in response.data


class TestAddCashflowRoute:
    """Tests for GET/POST /cashflow/add."""

    def test_add_form_renders(self, auth_client, sample_category):
        """GET /cashflow/add returns the add transaction form."""
        response = auth_client.get('/cashflow/add')
        assert response.status_code == 200
        assert b'csrf_token' in response.data

    def test_add_transaction_expense(self, auth_client, app, db, sample_category, sample_tag):
        """POST /cashflow/add creates a new expense transaction."""
        csrf = get_csrf_token(auth_client, '/cashflow/add')
        response = auth_client.post('/cashflow/add', data={
            'date': '2024-03-15',
            'amount': '250.75',
            'type': 'expense',
            'category_id': str(sample_category.id),
            'tags': [str(sample_tag.id)],
            'description': 'New test expense',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Transaction added successfully' in response.data

        # Verify in database
        with app.app_context():
            txn = CashflowTransaction.query.filter_by(description='New test expense').first()
            assert txn is not None
            assert txn.amount == 250.75
            assert txn.type == 'expense'
            assert txn.category_id == sample_category.id
            assert len(txn.tags) == 1

    def test_add_transaction_income(self, auth_client, app, db, sample_category):
        """POST /cashflow/add creates a new income transaction."""
        csrf = get_csrf_token(auth_client, '/cashflow/add')
        response = auth_client.post('/cashflow/add', data={
            'date': '2024-03-15',
            'amount': '5000.00',
            'type': 'income',
            'category_id': str(sample_category.id),
            'tags': [],
            'description': 'Salary payment',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Transaction added successfully' in response.data

        with app.app_context():
            txn = CashflowTransaction.query.filter_by(description='Salary payment').first()
            assert txn is not None
            assert txn.type == 'income'
            assert txn.amount == 5000.00

    def test_add_transaction_invalid_type(self, auth_client, sample_category):
        """POST /cashflow/add with invalid type shows error."""
        csrf = get_csrf_token(auth_client, '/cashflow/add')
        response = auth_client.post('/cashflow/add', data={
            'date': '2024-03-15',
            'amount': '100.00',
            'type': 'invalid_type',
            'category_id': str(sample_category.id),
            'tags': [],
            'description': 'Bad type',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid transaction type' in response.data

    def test_add_transaction_without_tags(self, auth_client, app, db, sample_category):
        """POST /cashflow/add without tags creates transaction with no tags."""
        csrf = get_csrf_token(auth_client, '/cashflow/add')
        response = auth_client.post('/cashflow/add', data={
            'date': '2024-04-01',
            'amount': '75.00',
            'type': 'expense',
            'category_id': str(sample_category.id),
            'description': 'No tags transaction',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Transaction added successfully' in response.data

        with app.app_context():
            txn = CashflowTransaction.query.filter_by(description='No tags transaction').first()
            assert txn is not None
            assert len(txn.tags) == 0


class TestEditCashflowRoute:
    """Tests for GET/POST /cashflow/edit/<id>."""

    def test_edit_form_renders(self, auth_client, sample_transaction):
        """GET /cashflow/edit/<id> returns the edit form with pre-filled data."""
        response = auth_client.get(f'/cashflow/edit/{sample_transaction.id}')
        assert response.status_code == 200
        assert b'csrf_token' in response.data
        assert b'Test transaction' in response.data

    def test_edit_transaction_success(self, auth_client, app, db, sample_transaction, sample_category):
        """POST /cashflow/edit/<id> updates the transaction."""
        csrf = get_csrf_token(auth_client, f'/cashflow/edit/{sample_transaction.id}')
        response = auth_client.post(f'/cashflow/edit/{sample_transaction.id}', data={
            'date': '2024-02-20',
            'amount': '200.00',
            'type': 'income',
            'category_id': str(sample_category.id),
            'description': 'Updated transaction',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Transaction updated successfully' in response.data

        with app.app_context():
            txn = CashflowTransaction.query.get(sample_transaction.id)
            assert txn.description == 'Updated transaction'
            assert txn.amount == 200.00
            assert txn.type == 'income'

    def test_edit_nonexistent_transaction(self, auth_client):
        """GET /cashflow/edit/99999 for nonexistent ID returns redirect (404 handler)."""
        response = auth_client.get('/cashflow/edit/99999', follow_redirects=False)
        # The app's 404 handler redirects to cashflow index
        assert response.status_code == 302

    def test_edit_transaction_update_tags(self, auth_client, app, db, sample_transaction, sample_category):
        """POST /cashflow/edit/<id> can update tags (remove all)."""
        csrf = get_csrf_token(auth_client, f'/cashflow/edit/{sample_transaction.id}')
        response = auth_client.post(f'/cashflow/edit/{sample_transaction.id}', data={
            'date': '2024-01-15',
            'amount': '100.50',
            'type': 'expense',
            'category_id': str(sample_category.id),
            'description': 'Test transaction',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Transaction updated successfully' in response.data

        with app.app_context():
            txn = CashflowTransaction.query.get(sample_transaction.id)
            assert len(txn.tags) == 0


class TestDeleteCashflowRoute:
    """Tests for POST /cashflow/delete/<id>."""

    def test_delete_transaction_success(self, auth_client, app, db, sample_transaction):
        """POST /cashflow/delete/<id> removes the transaction."""
        csrf = get_csrf_token(auth_client, '/cashflow/')
        txn_id = sample_transaction.id
        response = auth_client.post(f'/cashflow/delete/{txn_id}', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Transaction deleted successfully' in response.data

        with app.app_context():
            txn = CashflowTransaction.query.get(txn_id)
            assert txn is None

    def test_delete_nonexistent_transaction(self, auth_client):
        """POST /cashflow/delete/99999 for nonexistent ID redirects (404 handler)."""
        csrf = get_csrf_token(auth_client, '/cashflow/')
        response = auth_client.post('/cashflow/delete/99999', data={
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302


class TestBulkEditRoute:
    """Tests for POST /cashflow/bulk-edit."""

    def test_bulk_edit_category(self, auth_client, app, db, sample_transaction):
        """POST /cashflow/bulk-edit updates category for selected transactions."""
        # Create a new category to assign
        with app.app_context():
            new_cat = Category(name='Bulk Edit Category')
            db.session.add(new_cat)
            db.session.commit()
            new_cat_id = new_cat.id

        csrf = get_csrf_token(auth_client, '/cashflow/')
        response = auth_client.post('/cashflow/bulk-edit', data={
            'transaction_ids[]': [str(sample_transaction.id)],
            'category_id': str(new_cat_id),
            'tag_mode': 'replace',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'transaction(s) updated' in response.data

        with app.app_context():
            txn = CashflowTransaction.query.get(sample_transaction.id)
            assert txn.category_id == new_cat_id

    def test_bulk_edit_tags_replace(self, auth_client, app, db, sample_transaction):
        """POST /cashflow/bulk-edit replaces tags when tag_mode=replace."""
        with app.app_context():
            new_tag = Tag(name='Bulk Tag')
            db.session.add(new_tag)
            db.session.commit()
            new_tag_id = new_tag.id

        csrf = get_csrf_token(auth_client, '/cashflow/')
        response = auth_client.post('/cashflow/bulk-edit', data={
            'transaction_ids[]': [str(sample_transaction.id)],
            'tags[]': [str(new_tag_id)],
            'tag_mode': 'replace',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'transaction(s) updated' in response.data

        with app.app_context():
            txn = CashflowTransaction.query.get(sample_transaction.id)
            tag_ids = [t.id for t in txn.tags]
            assert new_tag_id in tag_ids

    def test_bulk_edit_tags_add(self, auth_client, app, db, sample_transaction, sample_tag):
        """POST /cashflow/bulk-edit adds tags when tag_mode=add."""
        with app.app_context():
            extra_tag = Tag(name='Extra Tag')
            db.session.add(extra_tag)
            db.session.commit()
            extra_tag_id = extra_tag.id

        csrf = get_csrf_token(auth_client, '/cashflow/')
        response = auth_client.post('/cashflow/bulk-edit', data={
            'transaction_ids[]': [str(sample_transaction.id)],
            'tags[]': [str(extra_tag_id)],
            'tag_mode': 'add',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'transaction(s) updated' in response.data

        with app.app_context():
            txn = CashflowTransaction.query.get(sample_transaction.id)
            tag_ids = [t.id for t in txn.tags]
            # Both original and new tag should be present
            assert sample_tag.id in tag_ids
            assert extra_tag_id in tag_ids

    def test_bulk_edit_no_transactions_selected(self, auth_client):
        """POST /cashflow/bulk-edit with no transaction IDs shows error."""
        csrf = get_csrf_token(auth_client, '/cashflow/')
        response = auth_client.post('/cashflow/bulk-edit', data={
            'tag_mode': 'replace',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'No transactions selected' in response.data


class TestImportRoute:
    """Tests for GET /cashflow/import."""

    def test_import_page_renders(self, auth_client):
        """GET /cashflow/import returns the import form page."""
        response = auth_client.get('/cashflow/import')
        assert response.status_code == 200


class TestCategoryDataApiRoute:
    """Tests for GET /cashflow/api/category-data."""

    def test_category_data_api_parent_mode(self, auth_client, sample_transaction):
        """GET /cashflow/api/category-data with parent mode returns JSON."""
        response = auth_client.get(
            '/cashflow/api/category-data?view_mode=parent'
            '&date_from=2024-01-01&date_to=2024-12-31'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'labels' in data
        assert 'values' in data

    def test_category_data_api_children_of_mode(
        self, auth_client, app, db, sample_category, sample_subcategory
    ):
        """GET /cashflow/api/category-data with children_of mode returns subcategory data."""
        with app.app_context():
            txn = CashflowTransaction(
                date=date(2024, 3, 1),
                type='expense',
                amount=75.0,
                description='Sub expense',
                category_id=sample_subcategory.id,
                source='manual',
            )
            db.session.add(txn)
            db.session.commit()

        response = auth_client.get(
            f'/cashflow/api/category-data?view_mode=children_of'
            f'&parent_id={sample_category.id}'
            f'&date_from=2024-01-01&date_to=2024-12-31'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'labels' in data
        assert 'parent_name' in data
        assert data['parent_name'] == 'Test Category'

    def test_category_data_api_children_of_no_parent_id(self, auth_client):
        """GET /cashflow/api/category-data children_of without parent_id returns empty."""
        response = auth_client.get(
            '/cashflow/api/category-data?view_mode=children_of'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['labels'] == []
        assert data['values'] == []

    def test_category_data_api_children_of_invalid_parent_id(self, auth_client):
        """GET /cashflow/api/category-data children_of with nonexistent parent returns empty."""
        response = auth_client.get(
            '/cashflow/api/category-data?view_mode=children_of&parent_id=99999'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['labels'] == []
        assert data['values'] == []

    def test_category_data_api_default_mode(self, auth_client):
        """GET /cashflow/api/category-data without view_mode uses default (child categories)."""
        response = auth_client.get('/cashflow/api/category-data?view_mode=child')
        assert response.status_code == 200
        data = response.get_json()
        assert 'labels' in data
        assert 'values' in data
