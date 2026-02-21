"""Integration tests for category routes (/categories)."""
import pytest
from datetime import date
from tests.conftest import get_csrf_token
from models.category import Category
from models.cashflow import CashflowTransaction


pytestmark = pytest.mark.integration


class TestCategoryIndexRoute:
    """Tests for GET /categories/."""

    def test_index_renders(self, auth_client):
        """GET /categories/ returns 200 with category list page."""
        response = auth_client.get('/categories/')
        assert response.status_code == 200

    def test_index_shows_categories(self, auth_client, sample_category):
        """GET /categories/ shows existing categories."""
        response = auth_client.get('/categories/')
        assert response.status_code == 200
        assert b'Test Category' in response.data

    def test_index_shows_only_parent_categories(self, auth_client, sample_category, sample_subcategory):
        """GET /categories/ lists parent categories (subcategories rendered under parents)."""
        response = auth_client.get('/categories/')
        assert response.status_code == 200
        assert b'Test Category' in response.data

    def test_index_requires_auth(self, client, admin_user):
        """GET /categories/ redirects to login when not authenticated."""
        response = client.get('/categories/', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers.get('Location', '')


class TestAddCategoryRoute:
    """Tests for GET/POST /categories/add."""

    def test_add_form_renders(self, auth_client):
        """GET /categories/add returns the add category form."""
        response = auth_client.get('/categories/add')
        assert response.status_code == 200
        assert b'csrf_token' in response.data

    def test_add_parent_category(self, auth_client, app, db):
        """POST /categories/add creates a new parent category."""
        csrf = get_csrf_token(auth_client, '/categories/add')
        response = auth_client.post('/categories/add', data={
            'name': 'New Parent Category',
            'parent_id': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Category added successfully' in response.data

        with app.app_context():
            cat = Category.query.filter_by(name='New Parent Category').first()
            assert cat is not None
            assert cat.parent_id is None

    def test_add_subcategory(self, auth_client, app, db, sample_category):
        """POST /categories/add creates a new subcategory under a parent."""
        csrf = get_csrf_token(auth_client, '/categories/add')
        response = auth_client.post('/categories/add', data={
            'name': 'New Subcategory',
            'parent_id': str(sample_category.id),
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Category added successfully' in response.data

        with app.app_context():
            sub = Category.query.filter_by(name='New Subcategory').first()
            assert sub is not None
            assert sub.parent_id == sample_category.id

    def test_add_duplicate_parent_category(self, auth_client, sample_category):
        """POST /categories/add with duplicate name+parent_id shows error."""
        csrf = get_csrf_token(auth_client, '/categories/add')
        response = auth_client.post('/categories/add', data={
            'name': 'Test Category',
            'parent_id': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'already exists' in response.data

    def test_add_duplicate_subcategory(self, auth_client, sample_category, sample_subcategory):
        """POST /categories/add with duplicate subcategory name under same parent shows error."""
        csrf = get_csrf_token(auth_client, '/categories/add')
        response = auth_client.post('/categories/add', data={
            'name': 'Test Subcategory',
            'parent_id': str(sample_category.id),
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'already exists' in response.data

    def test_add_same_name_different_parent_ok(self, auth_client, app, db, sample_category):
        """Same category name under different parents is allowed."""
        with app.app_context():
            other_parent = Category(name='Other Parent')
            db.session.add(other_parent)
            db.session.commit()
            other_parent_id = other_parent.id

        # First: add subcategory under sample_category
        csrf = get_csrf_token(auth_client, '/categories/add')
        auth_client.post('/categories/add', data={
            'name': 'Shared Name',
            'parent_id': str(sample_category.id),
            'csrf_token': csrf,
        }, follow_redirects=True)

        # Second: add subcategory with same name under different parent
        csrf = get_csrf_token(auth_client, '/categories/add')
        response = auth_client.post('/categories/add', data={
            'name': 'Shared Name',
            'parent_id': str(other_parent_id),
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Category added successfully' in response.data


class TestEditCategoryRoute:
    """Tests for GET/POST /categories/edit/<id>."""

    def test_edit_form_renders(self, auth_client, sample_category):
        """GET /categories/edit/<id> returns the edit form with pre-filled data."""
        response = auth_client.get(f'/categories/edit/{sample_category.id}')
        assert response.status_code == 200
        assert b'Test Category' in response.data
        assert b'csrf_token' in response.data

    def test_edit_category_success(self, auth_client, app, db, sample_category):
        """POST /categories/edit/<id> updates the category name."""
        csrf = get_csrf_token(auth_client, f'/categories/edit/{sample_category.id}')
        response = auth_client.post(f'/categories/edit/{sample_category.id}', data={
            'name': 'Updated Category',
            'parent_id': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Category updated successfully' in response.data

        with app.app_context():
            cat = Category.query.get(sample_category.id)
            assert cat.name == 'Updated Category'

    def test_edit_category_duplicate_name(self, auth_client, app, db, sample_category):
        """POST /categories/edit/<id> with duplicate name shows error."""
        with app.app_context():
            other = Category(name='Other Category')
            db.session.add(other)
            db.session.commit()
            other_id = other.id

        csrf = get_csrf_token(auth_client, f'/categories/edit/{other_id}')
        response = auth_client.post(f'/categories/edit/{other_id}', data={
            'name': 'Test Category',
            'parent_id': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'already exists' in response.data

    def test_edit_category_same_name_no_conflict(self, auth_client, sample_category):
        """POST /categories/edit/<id> keeping same name does not trigger duplicate error."""
        csrf = get_csrf_token(auth_client, f'/categories/edit/{sample_category.id}')
        response = auth_client.post(f'/categories/edit/{sample_category.id}', data={
            'name': 'Test Category',
            'parent_id': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Category updated successfully' in response.data

    def test_edit_nonexistent_category(self, auth_client):
        """GET /categories/edit/99999 for nonexistent ID redirects (404 handler)."""
        response = auth_client.get('/categories/edit/99999', follow_redirects=False)
        assert response.status_code == 302

    def test_edit_category_change_parent(self, auth_client, app, db, sample_subcategory, sample_category):
        """POST /categories/edit/<id> can change parent to make it a top-level category."""
        csrf = get_csrf_token(auth_client, f'/categories/edit/{sample_subcategory.id}')
        response = auth_client.post(f'/categories/edit/{sample_subcategory.id}', data={
            'name': 'Test Subcategory',
            'parent_id': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Category updated successfully' in response.data

        with app.app_context():
            sub = Category.query.get(sample_subcategory.id)
            assert sub.parent_id is None


class TestDeleteCategoryRoute:
    """Tests for POST /categories/delete/<id>."""

    def test_delete_category_success(self, auth_client, app, db, sample_category):
        """POST /categories/delete/<id> removes a category with no children or transactions."""
        csrf = get_csrf_token(auth_client, '/categories/')
        cat_id = sample_category.id
        response = auth_client.post(f'/categories/delete/{cat_id}', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Category deleted successfully' in response.data

        with app.app_context():
            cat = Category.query.get(cat_id)
            assert cat is None

    def test_delete_category_with_subcategories(self, auth_client, sample_category, sample_subcategory):
        """POST /categories/delete/<id> with subcategories shows protection error."""
        csrf = get_csrf_token(auth_client, '/categories/')
        response = auth_client.post(f'/categories/delete/{sample_category.id}', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'has subcategories' in response.data

    def test_delete_category_with_transactions(self, auth_client, sample_transaction, sample_category):
        """POST /categories/delete/<id> with transactions shows protection error."""
        csrf = get_csrf_token(auth_client, '/categories/')
        response = auth_client.post(f'/categories/delete/{sample_category.id}', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'associated transactions' in response.data

    def test_delete_nonexistent_category(self, auth_client):
        """POST /categories/delete/99999 for nonexistent ID redirects (404 handler)."""
        csrf = get_csrf_token(auth_client, '/categories/add')
        response = auth_client.post('/categories/delete/99999', data={
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302

    def test_delete_subcategory_without_transactions(self, auth_client, app, db, sample_subcategory):
        """POST /categories/delete/<id> for a subcategory with no transactions succeeds."""
        csrf = get_csrf_token(auth_client, '/categories/')
        sub_id = sample_subcategory.id
        response = auth_client.post(f'/categories/delete/{sub_id}', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Category deleted successfully' in response.data

        with app.app_context():
            sub = Category.query.get(sub_id)
            assert sub is None
