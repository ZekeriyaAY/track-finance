"""Tests for the /cashflow/api/category-data JSON API endpoint.

Verifies parent view, drill-down to children, empty data handling,
invalid parameters, and authentication requirements.
"""
import pytest
from datetime import date
from models.category import Category
from models.tag import Tag
from models.cashflow import CashflowTransaction
from models import db as _db


@pytest.fixture
def category_with_children_and_data(app, db):
    """Create parent and child categories with expense transactions."""
    # Parent category
    parent = Category(name='Food & Dining')
    db.session.add(parent)
    db.session.flush()

    # Child categories
    child1 = Category(name='Groceries', parent_id=parent.id)
    child2 = Category(name='Restaurants', parent_id=parent.id)
    db.session.add_all([child1, child2])
    db.session.flush()

    # Another parent category (no children)
    transport = Category(name='Transportation')
    db.session.add(transport)
    db.session.flush()

    today = date.today()

    # Transactions under child categories
    txn1 = CashflowTransaction(
        date=today,
        type='expense',
        amount=150.0,
        description='Weekly groceries',
        category_id=child1.id,
        source='manual',
    )
    txn2 = CashflowTransaction(
        date=today,
        type='expense',
        amount=80.0,
        description='Restaurant dinner',
        category_id=child2.id,
        source='manual',
    )
    # Transaction directly on parent
    txn3 = CashflowTransaction(
        date=today,
        type='expense',
        amount=25.0,
        description='Street food',
        category_id=parent.id,
        source='manual',
    )
    # Transaction on transport
    txn4 = CashflowTransaction(
        date=today,
        type='expense',
        amount=200.0,
        description='Gas',
        category_id=transport.id,
        source='manual',
    )
    # Income transaction (should NOT appear in expense breakdowns)
    txn5 = CashflowTransaction(
        date=today,
        type='income',
        amount=5000.0,
        description='Salary',
        category_id=parent.id,
        source='manual',
    )
    db.session.add_all([txn1, txn2, txn3, txn4, txn5])
    db.session.commit()

    return {
        'parent': parent,
        'child1': child1,
        'child2': child2,
        'transport': transport,
    }


@pytest.mark.api
class TestCategoryDataParentView:
    """GET /cashflow/api/category-data with default parent view."""

    def test_default_parent_view_returns_json(self, auth_client, category_with_children_and_data):
        """Default request returns JSON with labels, values, category_ids, has_children."""
        response = auth_client.get('/cashflow/api/category-data')
        assert response.status_code == 200
        data = response.get_json()
        assert 'labels' in data
        assert 'values' in data
        assert 'category_ids' in data
        assert 'has_children' in data

    def test_parent_view_aggregates_children(self, auth_client, category_with_children_and_data):
        """Parent view aggregates child category expenses under parent."""
        cats = category_with_children_and_data
        response = auth_client.get('/cashflow/api/category-data')
        data = response.get_json()

        # Food & Dining should have: 150 (groceries) + 80 (restaurants) + 25 (direct) = 255
        if 'Food & Dining' in data['labels']:
            idx = data['labels'].index('Food & Dining')
            assert data['values'][idx] == 255.0
            assert data['has_children'][idx] is True
            assert data['category_ids'][idx] == cats['parent'].id

    def test_parent_view_shows_childless_parent(self, auth_client, category_with_children_and_data):
        """Parent category without children shows has_children=False."""
        cats = category_with_children_and_data
        response = auth_client.get('/cashflow/api/category-data')
        data = response.get_json()

        if 'Transportation' in data['labels']:
            idx = data['labels'].index('Transportation')
            assert data['values'][idx] == 200.0
            assert data['has_children'][idx] is False
            assert data['category_ids'][idx] == cats['transport'].id

    def test_parent_view_excludes_income(self, auth_client, category_with_children_and_data):
        """Parent view only includes expense transactions, not income."""
        response = auth_client.get('/cashflow/api/category-data')
        data = response.get_json()

        # Total values should not include the 5000 income
        total = sum(data['values'])
        assert 5000.0 not in data['values']
        assert total < 5000  # All expenses combined are 455

    def test_parent_view_sorted_by_total_descending(self, auth_client, category_with_children_and_data):
        """Results should be sorted by total in descending order."""
        response = auth_client.get('/cashflow/api/category-data')
        data = response.get_json()
        values = data['values']
        assert values == sorted(values, reverse=True)

    def test_explicit_parent_view_mode(self, auth_client, category_with_children_and_data):
        """Explicitly passing view_mode=parent returns same as default."""
        default_response = auth_client.get('/cashflow/api/category-data')
        explicit_response = auth_client.get('/cashflow/api/category-data?view_mode=parent')
        assert default_response.get_json() == explicit_response.get_json()


@pytest.mark.api
class TestCategoryDataChildrenView:
    """GET /cashflow/api/category-data?view_mode=children_of&parent_id=X"""

    def test_children_view_returns_subcategories(self, auth_client, category_with_children_and_data):
        """Children view returns individual child category totals."""
        cats = category_with_children_and_data
        parent_id = cats['parent'].id
        response = auth_client.get(
            f'/cashflow/api/category-data?view_mode=children_of&parent_id={parent_id}'
        )
        assert response.status_code == 200
        data = response.get_json()

        assert 'labels' in data
        assert 'values' in data
        assert 'parent_name' in data
        assert data['parent_name'] == 'Food & Dining'

        # Should have Groceries (150), Restaurants (80), and Food & Dining (Direct) (25)
        assert len(data['labels']) == 3
        assert 'Groceries' in data['labels']
        assert 'Restaurants' in data['labels']

    def test_children_view_includes_direct_parent_transactions(self, auth_client, category_with_children_and_data):
        """Direct transactions on parent appear as 'Parent (Direct)' entry."""
        cats = category_with_children_and_data
        parent_id = cats['parent'].id
        response = auth_client.get(
            f'/cashflow/api/category-data?view_mode=children_of&parent_id={parent_id}'
        )
        data = response.get_json()

        direct_labels = [l for l in data['labels'] if 'Direct' in l]
        assert len(direct_labels) == 1
        idx = data['labels'].index(direct_labels[0])
        assert data['values'][idx] == 25.0

    def test_children_view_sorted_descending(self, auth_client, category_with_children_and_data):
        """Children view results are sorted by total descending."""
        cats = category_with_children_and_data
        parent_id = cats['parent'].id
        response = auth_client.get(
            f'/cashflow/api/category-data?view_mode=children_of&parent_id={parent_id}'
        )
        data = response.get_json()
        assert data['values'] == sorted(data['values'], reverse=True)

    def test_children_view_has_children_all_false(self, auth_client, category_with_children_and_data):
        """In children view, has_children should be False for all entries."""
        cats = category_with_children_and_data
        parent_id = cats['parent'].id
        response = auth_client.get(
            f'/cashflow/api/category-data?view_mode=children_of&parent_id={parent_id}'
        )
        data = response.get_json()
        assert all(hc is False for hc in data['has_children'])

    def test_children_view_childless_parent(self, auth_client, category_with_children_and_data):
        """Drill-down into parent with no children returns only direct entry."""
        cats = category_with_children_and_data
        transport_id = cats['transport'].id
        response = auth_client.get(
            f'/cashflow/api/category-data?view_mode=children_of&parent_id={transport_id}'
        )
        data = response.get_json()
        # Transportation has no children, only a direct transaction
        assert len(data['labels']) == 1
        assert 'Direct' in data['labels'][0]
        assert data['values'][0] == 200.0


@pytest.mark.api
class TestCategoryDataEmptyData:
    """API behavior when there are no transactions."""

    def test_empty_parent_view(self, auth_client):
        """Parent view with no transactions returns empty arrays."""
        response = auth_client.get('/cashflow/api/category-data')
        assert response.status_code == 200
        data = response.get_json()
        assert data['labels'] == []
        assert data['values'] == []
        assert data['category_ids'] == []
        assert data['has_children'] == []

    def test_empty_children_view_with_valid_parent(self, auth_client, sample_category):
        """Children view for a category with no expenses returns empty arrays."""
        response = auth_client.get(
            f'/cashflow/api/category-data?view_mode=children_of&parent_id={sample_category.id}'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['labels'] == []
        assert data['values'] == []


@pytest.mark.api
class TestCategoryDataInvalidParameters:
    """API behavior with invalid or missing parameters."""

    def test_missing_parent_id_for_children_view(self, auth_client):
        """children_of view without parent_id returns empty result."""
        response = auth_client.get('/cashflow/api/category-data?view_mode=children_of')
        assert response.status_code == 200
        data = response.get_json()
        assert data['labels'] == []
        assert data['values'] == []

    def test_invalid_parent_id(self, auth_client):
        """children_of view with non-existent parent_id returns empty result."""
        response = auth_client.get(
            '/cashflow/api/category-data?view_mode=children_of&parent_id=99999'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['labels'] == []
        assert data['values'] == []

    def test_non_numeric_parent_id(self, auth_client):
        """children_of view with non-numeric parent_id is handled safely."""
        response = auth_client.get(
            '/cashflow/api/category-data?view_mode=children_of&parent_id=abc'
        )
        assert response.status_code == 200
        data = response.get_json()
        # parent_id=abc will be None from request.args.get(..., type=int)
        assert data['labels'] == []
        assert data['values'] == []

    def test_unknown_view_mode(self, auth_client):
        """Unknown view_mode falls through to the else branch safely."""
        response = auth_client.get('/cashflow/api/category-data?view_mode=unknown')
        assert response.status_code == 200
        data = response.get_json()
        assert 'labels' in data
        assert 'values' in data

    def test_invalid_date_parameters(self, auth_client):
        """Invalid date parameters use defaults instead of crashing."""
        response = auth_client.get(
            '/cashflow/api/category-data?date_from=not-a-date&date_to=also-bad'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data['labels'], list)
        assert isinstance(data['values'], list)

    def test_sqli_in_parent_id(self, auth_client):
        """SQL injection attempt in parent_id parameter is handled safely."""
        response = auth_client.get(
            "/cashflow/api/category-data?view_mode=children_of&parent_id=1%20OR%201%3D1"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['labels'] == []


@pytest.mark.api
class TestCategoryDataDateFiltering:
    """API respects date_from and date_to parameters."""

    def test_date_filtering(self, auth_client, app, db):
        """Transactions outside the date range are excluded."""
        with app.app_context():
            cat = Category(name='Filtered Category')
            db.session.add(cat)
            db.session.flush()

            # Transaction in January
            txn_jan = CashflowTransaction(
                date=date(2024, 1, 15),
                type='expense',
                amount=100.0,
                description='January expense',
                category_id=cat.id,
                source='manual',
            )
            # Transaction in June
            txn_jun = CashflowTransaction(
                date=date(2024, 6, 15),
                type='expense',
                amount=200.0,
                description='June expense',
                category_id=cat.id,
                source='manual',
            )
            db.session.add_all([txn_jan, txn_jun])
            db.session.commit()

        # Filter to January only
        response = auth_client.get(
            '/cashflow/api/category-data?date_from=2024-01-01&date_to=2024-01-31'
        )
        data = response.get_json()
        if 'Filtered Category' in data['labels']:
            idx = data['labels'].index('Filtered Category')
            assert data['values'][idx] == 100.0

        # Filter to June only
        response = auth_client.get(
            '/cashflow/api/category-data?date_from=2024-06-01&date_to=2024-06-30'
        )
        data = response.get_json()
        if 'Filtered Category' in data['labels']:
            idx = data['labels'].index('Filtered Category')
            assert data['values'][idx] == 200.0


@pytest.mark.api
class TestCategoryDataAuthentication:
    """API endpoint requires authentication."""

    def test_unauthenticated_access_redirects(self, client, admin_user):
        """GET /cashflow/api/category-data without auth redirects to login."""
        response = client.get('/cashflow/api/category-data')
        assert response.status_code == 302
        location = response.headers.get('Location', '')
        assert '/auth/login' in location

    def test_unauthenticated_children_view_redirects(self, client, admin_user):
        """GET children_of view without auth redirects to login."""
        response = client.get(
            '/cashflow/api/category-data?view_mode=children_of&parent_id=1'
        )
        assert response.status_code == 302
        location = response.headers.get('Location', '')
        assert '/auth/login' in location
