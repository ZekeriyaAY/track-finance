"""Integration tests for investment type routes (/investment-types)."""
import pytest
from datetime import datetime
from tests.conftest import get_csrf_token
from models.investment import InvestmentType, InvestmentTransaction


pytestmark = pytest.mark.integration


class TestInvestmentTypeIndexRoute:
    """Tests for GET /investment-types/."""

    def test_index_renders(self, auth_client):
        """GET /investment-types/ returns 200 with investment type list page."""
        response = auth_client.get('/investment-types/')
        assert response.status_code == 200

    def test_index_shows_investment_types(self, auth_client, sample_investment_type):
        """GET /investment-types/ shows existing investment types."""
        response = auth_client.get('/investment-types/')
        assert response.status_code == 200
        assert b'Test Stock' in response.data

    def test_index_shows_only_parent_types(self, auth_client, app, db, sample_investment_type):
        """GET /investment-types/ lists parent types (children rendered under parents)."""
        with app.app_context():
            child = InvestmentType(
                name='Child Type',
                code='child_type',
                icon='fas fa-coins',
                color='#10B981',
                parent_id=sample_investment_type.id,
            )
            db.session.add(child)
            db.session.commit()

        response = auth_client.get('/investment-types/')
        assert response.status_code == 200
        assert b'Test Stock' in response.data

    def test_index_requires_auth(self, client, admin_user):
        """GET /investment-types/ redirects to login when not authenticated."""
        response = client.get('/investment-types/', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers.get('Location', '')


class TestAddInvestmentTypeRoute:
    """Tests for GET/POST /investment-types/add."""

    def test_add_form_renders(self, auth_client):
        """GET /investment-types/add returns the add investment type form."""
        response = auth_client.get('/investment-types/add')
        assert response.status_code == 200
        assert b'csrf_token' in response.data

    def test_add_parent_investment_type(self, auth_client, app, db):
        """POST /investment-types/add creates a new parent investment type."""
        csrf = get_csrf_token(auth_client, '/investment-types/add')
        response = auth_client.post('/investment-types/add', data={
            'name': 'Cryptocurrency',
            'code': 'crypto',
            'icon': 'fas fa-bitcoin-sign',
            'color': '#F59E0B',
            'parent_id': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Investment type added successfully' in response.data

        with app.app_context():
            inv_type = InvestmentType.query.filter_by(name='Cryptocurrency').first()
            assert inv_type is not None
            assert inv_type.code == 'crypto'
            assert inv_type.parent_id is None

    def test_add_child_investment_type(self, auth_client, app, db, sample_investment_type):
        """POST /investment-types/add creates a child investment type."""
        csrf = get_csrf_token(auth_client, '/investment-types/add')
        response = auth_client.post('/investment-types/add', data={
            'name': 'Tech Stock',
            'code': 'tech_stock',
            'icon': 'fas fa-microchip',
            'color': '#6366F1',
            'parent_id': str(sample_investment_type.id),
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Investment type added successfully' in response.data

        with app.app_context():
            child = InvestmentType.query.filter_by(name='Tech Stock').first()
            assert child is not None
            assert child.parent_id == sample_investment_type.id

    def test_add_duplicate_investment_type(self, auth_client, sample_investment_type):
        """POST /investment-types/add with duplicate name shows error."""
        csrf = get_csrf_token(auth_client, '/investment-types/add')
        response = auth_client.post('/investment-types/add', data={
            'name': 'Test Stock',
            'code': 'test_stock_dup',
            'icon': 'fas fa-chart-line',
            'color': '#3B82F6',
            'parent_id': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'already exists' in response.data

    def test_add_investment_type_redirects_to_index(self, auth_client, app, db):
        """POST /investment-types/add redirects to investment-types index."""
        csrf = get_csrf_token(auth_client, '/investment-types/add')
        response = auth_client.post('/investment-types/add', data={
            'name': 'Redirect Type',
            'code': 'redirect_type',
            'icon': 'fas fa-arrow-right',
            'color': '#EC4899',
            'parent_id': '',
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/investment-types/' in response.headers.get('Location', '')


class TestEditInvestmentTypeRoute:
    """Tests for GET/POST /investment-types/edit/<id>."""

    def test_edit_form_renders(self, auth_client, sample_investment_type):
        """GET /investment-types/edit/<id> returns the edit form with pre-filled data."""
        response = auth_client.get(f'/investment-types/edit/{sample_investment_type.id}')
        assert response.status_code == 200
        assert b'Test Stock' in response.data
        assert b'csrf_token' in response.data

    def test_edit_investment_type_success(self, auth_client, app, db, sample_investment_type):
        """POST /investment-types/edit/<id> updates the investment type."""
        csrf = get_csrf_token(auth_client, f'/investment-types/edit/{sample_investment_type.id}')
        response = auth_client.post(f'/investment-types/edit/{sample_investment_type.id}', data={
            'name': 'Updated Stock',
            'code': 'updated_stock',
            'icon': 'fas fa-chart-area',
            'color': '#EF4444',
            'parent_id': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Investment type updated successfully' in response.data

        with app.app_context():
            inv_type = InvestmentType.query.get(sample_investment_type.id)
            assert inv_type.name == 'Updated Stock'
            assert inv_type.code == 'updated_stock'
            assert inv_type.color == '#EF4444'

    def test_edit_investment_type_duplicate_name(self, auth_client, app, db, sample_investment_type):
        """POST /investment-types/edit/<id> with duplicate name shows error."""
        with app.app_context():
            other = InvestmentType(
                name='Other Type', code='other_type',
                icon='fas fa-coins', color='#10B981'
            )
            db.session.add(other)
            db.session.commit()
            other_id = other.id

        csrf = get_csrf_token(auth_client, f'/investment-types/edit/{other_id}')
        response = auth_client.post(f'/investment-types/edit/{other_id}', data={
            'name': 'Test Stock',
            'code': 'other_type',
            'icon': 'fas fa-coins',
            'color': '#10B981',
            'parent_id': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'already exists' in response.data

    def test_edit_investment_type_same_name_no_conflict(self, auth_client, sample_investment_type):
        """POST /investment-types/edit/<id> keeping same name does not trigger duplicate."""
        csrf = get_csrf_token(auth_client, f'/investment-types/edit/{sample_investment_type.id}')
        response = auth_client.post(f'/investment-types/edit/{sample_investment_type.id}', data={
            'name': 'Test Stock',
            'code': 'test_stock',
            'icon': 'fas fa-chart-line',
            'color': '#3B82F6',
            'parent_id': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Investment type updated successfully' in response.data

    def test_edit_nonexistent_investment_type(self, auth_client):
        """GET /investment-types/edit/99999 for nonexistent ID redirects (404 handler)."""
        response = auth_client.get('/investment-types/edit/99999', follow_redirects=False)
        assert response.status_code == 302

    def test_edit_investment_type_change_parent(self, auth_client, app, db, sample_investment_type):
        """POST /investment-types/edit/<id> can change parent relationship."""
        with app.app_context():
            child = InvestmentType(
                name='Child To Move',
                code='child_move',
                icon='fas fa-arrows-alt',
                color='#A855F7',
                parent_id=sample_investment_type.id,
            )
            db.session.add(child)
            db.session.commit()
            child_id = child.id

        # Change the child to be a parent (remove parent_id)
        csrf = get_csrf_token(auth_client, f'/investment-types/edit/{child_id}')
        response = auth_client.post(f'/investment-types/edit/{child_id}', data={
            'name': 'Child To Move',
            'code': 'child_move',
            'icon': 'fas fa-arrows-alt',
            'color': '#A855F7',
            'parent_id': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Investment type updated successfully' in response.data

        with app.app_context():
            moved = InvestmentType.query.get(child_id)
            assert moved.parent_id is None


class TestDeleteInvestmentTypeRoute:
    """Tests for POST /investment-types/delete/<id>."""

    def test_delete_investment_type_success(self, auth_client, app, db, sample_investment_type):
        """POST /investment-types/delete/<id> removes a type with no children or investments."""
        csrf = get_csrf_token(auth_client, '/investment-types/')
        type_id = sample_investment_type.id
        response = auth_client.post(f'/investment-types/delete/{type_id}', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Investment type deleted successfully' in response.data

        with app.app_context():
            inv_type = InvestmentType.query.get(type_id)
            assert inv_type is None

    def test_delete_investment_type_with_children(self, auth_client, app, db, sample_investment_type):
        """POST /investment-types/delete/<id> with children shows protection error."""
        with app.app_context():
            child = InvestmentType(
                name='Child Block Delete',
                code='child_block',
                icon='fas fa-lock',
                color='#DC2626',
                parent_id=sample_investment_type.id,
            )
            db.session.add(child)
            db.session.commit()

        csrf = get_csrf_token(auth_client, '/investment-types/')
        response = auth_client.post(
            f'/investment-types/delete/{sample_investment_type.id}',
            data={'csrf_token': csrf},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b'has subtypes' in response.data

    def test_delete_investment_type_with_investments(self, auth_client, sample_investment_type, sample_investment):
        """POST /investment-types/delete/<id> with investments shows protection error."""
        csrf = get_csrf_token(auth_client, '/investment-types/')
        response = auth_client.post(
            f'/investment-types/delete/{sample_investment_type.id}',
            data={'csrf_token': csrf},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b'associated investments' in response.data

    def test_delete_nonexistent_investment_type(self, auth_client):
        """POST /investment-types/delete/99999 for nonexistent ID redirects (404 handler)."""
        csrf = get_csrf_token(auth_client, '/investment-types/add')
        response = auth_client.post('/investment-types/delete/99999', data={
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302

    def test_delete_child_investment_type_without_investments(self, auth_client, app, db, sample_investment_type):
        """POST /investment-types/delete/<id> for child type with no investments succeeds."""
        with app.app_context():
            child = InvestmentType(
                name='Deletable Child',
                code='deletable_child',
                icon='fas fa-trash',
                color='#F87171',
                parent_id=sample_investment_type.id,
            )
            db.session.add(child)
            db.session.commit()
            child_id = child.id

        csrf = get_csrf_token(auth_client, '/investment-types/')
        response = auth_client.post(f'/investment-types/delete/{child_id}', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Investment type deleted successfully' in response.data

        with app.app_context():
            deleted = InvestmentType.query.get(child_id)
            assert deleted is None

    def test_delete_investment_type_redirects_to_index(self, auth_client, app, db):
        """POST /investment-types/delete/<id> redirects to investment-types index."""
        with app.app_context():
            temp = InvestmentType(
                name='Temp Type', code='temp_type',
                icon='fas fa-clock', color='#F59E0B'
            )
            db.session.add(temp)
            db.session.commit()
            temp_id = temp.id

        csrf = get_csrf_token(auth_client, '/investment-types/')
        response = auth_client.post(f'/investment-types/delete/{temp_id}', data={
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/investment-types/' in response.headers.get('Location', '')
