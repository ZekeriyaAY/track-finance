"""Integration tests for investment routes (/investments)."""
import pytest
from datetime import datetime
from tests.conftest import get_csrf_token
from models.investment import InvestmentTransaction, InvestmentType


pytestmark = pytest.mark.integration


class TestInvestmentIndexRoute:
    """Tests for GET /investments/."""

    def test_index_renders(self, auth_client):
        """GET /investments/ returns 200 with investment list page."""
        response = auth_client.get('/investments/')
        assert response.status_code == 200

    def test_index_shows_investments(self, auth_client, sample_investment):
        """GET /investments/ shows existing investment transactions."""
        response = auth_client.get('/investments/')
        assert response.status_code == 200
        assert b'Test investment' in response.data

    def test_index_filter_by_investment_type(self, auth_client, sample_investment, sample_investment_type):
        """GET /investments/ filtered by investment_type_id shows matching investments."""
        response = auth_client.get(
            f'/investments/?investment_type_id={sample_investment_type.id}'
        )
        assert response.status_code == 200
        assert b'Test investment' in response.data

    def test_index_filter_by_transaction_type_buy(self, auth_client, sample_investment):
        """GET /investments/ filtered by transaction_type=buy shows buy transactions."""
        response = auth_client.get('/investments/?transaction_type=buy')
        assert response.status_code == 200
        assert b'Test investment' in response.data

    def test_index_filter_by_transaction_type_sell(self, auth_client, sample_investment):
        """GET /investments/ filtered by transaction_type=sell excludes buy transactions."""
        response = auth_client.get('/investments/?transaction_type=sell')
        assert response.status_code == 200
        # The sample investment is a 'buy', so it should not appear
        assert b'Test investment' not in response.data

    def test_index_filter_by_date_range(self, auth_client, sample_investment):
        """GET /investments/ filtered by date range shows matching investments."""
        response = auth_client.get(
            '/investments/?date_from=2024-01-01&date_to=2024-01-31'
        )
        assert response.status_code == 200
        assert b'Test investment' in response.data

    def test_index_filter_by_date_range_excludes(self, auth_client, sample_investment):
        """GET /investments/ with out-of-range dates excludes investments."""
        response = auth_client.get(
            '/investments/?date_from=2025-06-01&date_to=2025-12-31'
        )
        assert response.status_code == 200
        assert b'Test investment' not in response.data

    def test_index_filter_invalid_transaction_type_ignored(self, auth_client, sample_investment):
        """GET /investments/ with invalid transaction_type is ignored (shows all)."""
        response = auth_client.get('/investments/?transaction_type=invalid')
        assert response.status_code == 200
        # Invalid type is not in ['buy', 'sell'], so no filter applied
        assert b'Test investment' in response.data

    def test_index_filter_by_parent_type_includes_subtypes(
        self, auth_client, app, db, sample_investment_type
    ):
        """Filtering by parent investment type also includes subtype investments."""
        with app.app_context():
            subtype = InvestmentType(
                name='Test Substock',
                code='test_substock',
                icon='fas fa-chart-bar',
                color='#EF4444',
                parent_id=sample_investment_type.id,
            )
            db.session.add(subtype)
            db.session.flush()

            inv = InvestmentTransaction(
                investment_type_id=subtype.id,
                transaction_date=datetime(2024, 2, 1),
                transaction_type='buy',
                price=200.0,
                quantity=5.0,
                description='Subtype investment',
            )
            db.session.add(inv)
            db.session.commit()

        response = auth_client.get(
            f'/investments/?investment_type_id={sample_investment_type.id}'
        )
        assert response.status_code == 200
        assert b'Subtype investment' in response.data

    def test_index_requires_auth(self, client, admin_user):
        """GET /investments/ redirects to login when not authenticated."""
        response = client.get('/investments/', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers.get('Location', '')


class TestAddInvestmentRoute:
    """Tests for GET/POST /investments/add."""

    def test_add_form_renders(self, auth_client, sample_investment_type):
        """GET /investments/add returns the add investment form."""
        response = auth_client.get('/investments/add')
        assert response.status_code == 200
        assert b'csrf_token' in response.data

    def test_add_investment_buy(self, auth_client, app, db, sample_investment_type):
        """POST /investments/add creates a new buy investment transaction."""
        csrf = get_csrf_token(auth_client, '/investments/add')
        response = auth_client.post('/investments/add', data={
            'investment_type_id': str(sample_investment_type.id),
            'transaction_date': '2024-05-15',
            'transaction_type': 'buy',
            'price': '250.50',
            'quantity': '20',
            'description': 'New stock purchase',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Investment transaction added successfully' in response.data

        with app.app_context():
            inv = InvestmentTransaction.query.filter_by(
                description='New stock purchase'
            ).first()
            assert inv is not None
            assert inv.price == 250.50
            assert inv.quantity == 20.0
            assert inv.total_amount == 250.50 * 20.0
            assert inv.transaction_type == 'buy'

    def test_add_investment_sell(self, auth_client, app, db, sample_investment_type):
        """POST /investments/add creates a new sell investment transaction."""
        csrf = get_csrf_token(auth_client, '/investments/add')
        response = auth_client.post('/investments/add', data={
            'investment_type_id': str(sample_investment_type.id),
            'transaction_date': '2024-06-01',
            'transaction_type': 'sell',
            'price': '300.00',
            'quantity': '5',
            'description': 'Stock sale',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Investment transaction added successfully' in response.data

        with app.app_context():
            inv = InvestmentTransaction.query.filter_by(description='Stock sale').first()
            assert inv is not None
            assert inv.transaction_type == 'sell'
            assert inv.total_amount == 300.00 * 5.0

    def test_add_investment_invalid_type(self, auth_client, sample_investment_type):
        """POST /investments/add with invalid transaction_type shows error."""
        csrf = get_csrf_token(auth_client, '/investments/add')
        response = auth_client.post('/investments/add', data={
            'investment_type_id': str(sample_investment_type.id),
            'transaction_date': '2024-05-15',
            'transaction_type': 'invalid_type',
            'price': '100.00',
            'quantity': '10',
            'description': 'Bad type',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid transaction type' in response.data

    def test_add_investment_total_amount_calculated(self, auth_client, app, db, sample_investment_type):
        """POST /investments/add auto-calculates total_amount from price * quantity."""
        csrf = get_csrf_token(auth_client, '/investments/add')
        auth_client.post('/investments/add', data={
            'investment_type_id': str(sample_investment_type.id),
            'transaction_date': '2024-07-01',
            'transaction_type': 'buy',
            'price': '123.45',
            'quantity': '7',
            'description': 'Calc test',
            'csrf_token': csrf,
        }, follow_redirects=True)

        with app.app_context():
            inv = InvestmentTransaction.query.filter_by(description='Calc test').first()
            assert inv is not None
            assert abs(float(inv.total_amount) - (123.45 * 7)) < 0.01

    def test_add_investment_redirects_to_index(self, auth_client, sample_investment_type):
        """POST /investments/add redirects to investment index."""
        csrf = get_csrf_token(auth_client, '/investments/add')
        response = auth_client.post('/investments/add', data={
            'investment_type_id': str(sample_investment_type.id),
            'transaction_date': '2024-08-01',
            'transaction_type': 'buy',
            'price': '100',
            'quantity': '1',
            'description': 'Redirect test',
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/investments/' in response.headers.get('Location', '')


class TestEditInvestmentRoute:
    """Tests for GET/POST /investments/edit/<id>."""

    def test_edit_form_renders(self, auth_client, sample_investment):
        """GET /investments/edit/<id> returns the edit form with pre-filled data."""
        response = auth_client.get(f'/investments/edit/{sample_investment.id}')
        assert response.status_code == 200
        assert b'Test investment' in response.data
        assert b'csrf_token' in response.data

    def test_edit_investment_success(self, auth_client, app, db, sample_investment, sample_investment_type):
        """POST /investments/edit/<id> updates the investment transaction."""
        csrf = get_csrf_token(auth_client, f'/investments/edit/{sample_investment.id}')
        response = auth_client.post(f'/investments/edit/{sample_investment.id}', data={
            'investment_type_id': str(sample_investment_type.id),
            'transaction_date': '2024-03-20',
            'transaction_type': 'sell',
            'price': '175.00',
            'quantity': '8',
            'description': 'Updated investment',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Investment transaction updated successfully' in response.data

        with app.app_context():
            inv = InvestmentTransaction.query.get(sample_investment.id)
            assert inv.description == 'Updated investment'
            assert inv.transaction_type == 'sell'
            assert inv.price == 175.00
            assert inv.quantity == 8.0

    def test_edit_investment_recalculates_total(self, auth_client, app, db, sample_investment, sample_investment_type):
        """POST /investments/edit/<id> recalculates total_amount from updated price * quantity."""
        csrf = get_csrf_token(auth_client, f'/investments/edit/{sample_investment.id}')
        auth_client.post(f'/investments/edit/{sample_investment.id}', data={
            'investment_type_id': str(sample_investment_type.id),
            'transaction_date': '2024-01-15',
            'transaction_type': 'buy',
            'price': '200.00',
            'quantity': '12',
            'description': 'Recalc test',
            'csrf_token': csrf,
        }, follow_redirects=True)

        with app.app_context():
            inv = InvestmentTransaction.query.get(sample_investment.id)
            assert abs(float(inv.total_amount) - (200.00 * 12)) < 0.01

    def test_edit_nonexistent_investment(self, auth_client):
        """GET /investments/edit/99999 for nonexistent ID redirects (404 handler)."""
        response = auth_client.get('/investments/edit/99999', follow_redirects=False)
        assert response.status_code == 302

    def test_edit_investment_redirects_to_index(self, auth_client, sample_investment, sample_investment_type):
        """POST /investments/edit/<id> redirects to investment index."""
        csrf = get_csrf_token(auth_client, f'/investments/edit/{sample_investment.id}')
        response = auth_client.post(f'/investments/edit/{sample_investment.id}', data={
            'investment_type_id': str(sample_investment_type.id),
            'transaction_date': '2024-01-15',
            'transaction_type': 'buy',
            'price': '150',
            'quantity': '10',
            'description': 'Test investment',
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/investments/' in response.headers.get('Location', '')


class TestDeleteInvestmentRoute:
    """Tests for POST /investments/delete/<id>."""

    def test_delete_investment_success(self, auth_client, app, db, sample_investment):
        """POST /investments/delete/<id> removes the investment transaction."""
        csrf = get_csrf_token(auth_client, '/investments/')
        inv_id = sample_investment.id
        response = auth_client.post(f'/investments/delete/{inv_id}', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Investment transaction deleted successfully' in response.data

        with app.app_context():
            inv = InvestmentTransaction.query.get(inv_id)
            assert inv is None

    def test_delete_nonexistent_investment(self, auth_client):
        """POST /investments/delete/99999 for nonexistent ID redirects (404 handler)."""
        csrf = get_csrf_token(auth_client, '/investments/add')
        response = auth_client.post('/investments/delete/99999', data={
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302

    def test_delete_investment_redirects_to_index(self, auth_client, app, db, sample_investment_type):
        """POST /investments/delete/<id> redirects to investment index."""
        with app.app_context():
            inv = InvestmentTransaction(
                investment_type_id=sample_investment_type.id,
                transaction_date=datetime(2024, 4, 1),
                transaction_type='buy',
                price=50.0,
                quantity=2.0,
                description='Delete redirect test',
            )
            db.session.add(inv)
            db.session.commit()
            inv_id = inv.id

        csrf = get_csrf_token(auth_client, '/investments/')
        response = auth_client.post(f'/investments/delete/{inv_id}', data={
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/investments/' in response.headers.get('Location', '')
