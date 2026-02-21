"""Integration tests for settings routes (/settings)."""
import pytest
from tests.conftest import get_csrf_token
from models.settings import Settings
from models.category import Category
from models.tag import Tag
from models.investment import InvestmentType, InvestmentTransaction
from models.cashflow import CashflowTransaction


pytestmark = pytest.mark.integration


class TestSettingsIndexRoute:
    """Tests for GET /settings/."""

    def test_index_renders(self, auth_client):
        """GET /settings/ returns 200 with settings page."""
        response = auth_client.get('/settings/')
        assert response.status_code == 200

    def test_index_shows_pgadmin_url(self, auth_client):
        """GET /settings/ page includes pgadmin URL section."""
        response = auth_client.get('/settings/')
        assert response.status_code == 200
        # Default pgadmin url should be present
        assert b'pgadmin' in response.data.lower() or b'PgAdmin' in response.data

    def test_index_requires_auth(self, client, admin_user):
        """GET /settings/ redirects to login when not authenticated."""
        response = client.get('/settings/', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers.get('Location', '')


class TestUpdatePgAdminUrlRoute:
    """Tests for POST /settings/update-pgadmin-url."""

    def test_update_pgadmin_url_success(self, auth_client, app, db):
        """POST /settings/update-pgadmin-url updates the URL."""
        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/update-pgadmin-url', data={
            'pgadmin_url': 'http://myserver:5050',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'PgAdmin URL updated successfully' in response.data

        with app.app_context():
            url = Settings.get_setting('pgadmin_url')
            assert url == 'http://myserver:5050'

    def test_update_pgadmin_url_auto_prefix(self, auth_client, app, db):
        """POST /settings/update-pgadmin-url auto-prefixes http:// if missing."""
        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/update-pgadmin-url', data={
            'pgadmin_url': 'myserver:5050',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'PgAdmin URL updated successfully' in response.data

        with app.app_context():
            url = Settings.get_setting('pgadmin_url')
            assert url == 'http://myserver:5050'

    def test_update_pgadmin_url_https_preserved(self, auth_client, app, db):
        """POST /settings/update-pgadmin-url preserves https:// prefix."""
        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/update-pgadmin-url', data={
            'pgadmin_url': 'https://secure.server:5050',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200

        with app.app_context():
            url = Settings.get_setting('pgadmin_url')
            assert url == 'https://secure.server:5050'

    def test_update_pgadmin_url_empty(self, auth_client):
        """POST /settings/update-pgadmin-url with empty URL shows error."""
        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/update-pgadmin-url', data={
            'pgadmin_url': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'cannot be empty' in response.data

    def test_update_pgadmin_url_whitespace_only(self, auth_client):
        """POST /settings/update-pgadmin-url with whitespace-only URL shows error."""
        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/update-pgadmin-url', data={
            'pgadmin_url': '   ',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'cannot be empty' in response.data

    def test_update_pgadmin_url_redirects_to_settings(self, auth_client):
        """POST /settings/update-pgadmin-url redirects to settings index."""
        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/update-pgadmin-url', data={
            'pgadmin_url': 'http://example.com:5050',
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/settings/' in response.headers.get('Location', '')


class TestCreateDefaultCategoriesRoute:
    """Tests for POST /settings/create-default-categories."""

    def test_create_default_categories(self, auth_client, app, db):
        """POST /settings/create-default-categories creates categories."""
        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/create-default-categories', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Default categories created successfully' in response.data

        with app.app_context():
            count = Category.query.count()
            assert count > 0

    def test_create_default_categories_redirects(self, auth_client):
        """POST /settings/create-default-categories redirects to settings index."""
        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/create-default-categories', data={
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/settings/' in response.headers.get('Location', '')


class TestCreateDefaultTagsRoute:
    """Tests for POST /settings/create-default-tags."""

    def test_create_default_tags(self, auth_client, app, db):
        """POST /settings/create-default-tags creates tags."""
        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/create-default-tags', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Default tags created successfully' in response.data

        with app.app_context():
            count = Tag.query.count()
            assert count > 0

    def test_create_default_tags_redirects(self, auth_client):
        """POST /settings/create-default-tags redirects to settings index."""
        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/create-default-tags', data={
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/settings/' in response.headers.get('Location', '')


class TestCreateDefaultInvestmentTypesRoute:
    """Tests for POST /settings/create-default-investment-types."""

    def test_create_default_investment_types(self, auth_client, app, db):
        """POST /settings/create-default-investment-types creates investment types."""
        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/create-default-investment-types', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Default investment types created successfully' in response.data

        with app.app_context():
            count = InvestmentType.query.count()
            assert count > 0

    def test_create_default_investment_types_redirects(self, auth_client):
        """POST /settings/create-default-investment-types redirects to settings index."""
        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/create-default-investment-types', data={
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/settings/' in response.headers.get('Location', '')


class TestCreateDummyDataRoute:
    """Tests for POST /settings/create-dummy-data."""

    def test_create_dummy_data(self, auth_client, app, db):
        """POST /settings/create-dummy-data creates dummy transactions."""
        # First create default categories, tags, and investment types
        # because dummy data depends on them
        csrf = get_csrf_token(auth_client, '/settings/')
        auth_client.post('/settings/create-default-categories', data={
            'csrf_token': csrf,
        }, follow_redirects=True)

        csrf = get_csrf_token(auth_client, '/settings/')
        auth_client.post('/settings/create-default-tags', data={
            'csrf_token': csrf,
        }, follow_redirects=True)

        csrf = get_csrf_token(auth_client, '/settings/')
        auth_client.post('/settings/create-default-investment-types', data={
            'csrf_token': csrf,
        }, follow_redirects=True)

        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/create-dummy-data', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Dummy data created successfully' in response.data

        with app.app_context():
            cashflow_count = CashflowTransaction.query.count()
            assert cashflow_count > 0

    def test_create_dummy_data_redirects(self, auth_client):
        """POST /settings/create-dummy-data redirects to settings index."""
        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/create-dummy-data', data={
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/settings/' in response.headers.get('Location', '')


class TestResetDatabaseRoute:
    """Tests for POST /settings/reset-database."""

    def test_reset_database_clears_data(self, auth_client, app, db, sample_transaction, sample_investment):
        """POST /settings/reset-database removes all data from tables."""
        # Verify data exists first
        with app.app_context():
            assert CashflowTransaction.query.count() > 0

        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/reset-database', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Database data cleared successfully' in response.data

        # Verify data was cleared
        with app.app_context():
            assert CashflowTransaction.query.count() == 0
            assert Category.query.count() == 0
            assert Tag.query.count() == 0
            assert InvestmentTransaction.query.count() == 0
            assert InvestmentType.query.count() == 0

    def test_reset_database_handles_empty_db(self, auth_client, app, db):
        """POST /settings/reset-database on empty database succeeds gracefully."""
        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/reset-database', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Database data cleared successfully' in response.data

    def test_reset_database_redirects(self, auth_client):
        """POST /settings/reset-database redirects to settings index."""
        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/reset-database', data={
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/settings/' in response.headers.get('Location', '')

    def test_reset_database_preserves_users(self, auth_client, app, db, sample_transaction):
        """POST /settings/reset-database does NOT delete users (auth still works)."""
        csrf = get_csrf_token(auth_client, '/settings/')
        auth_client.post('/settings/reset-database', data={
            'csrf_token': csrf,
        }, follow_redirects=True)

        # Auth should still work -- user was not deleted
        from models.user import User
        with app.app_context():
            assert User.query.count() > 0

    def test_reset_database_preserves_settings(self, auth_client, app, db):
        """POST /settings/reset-database does NOT delete settings entries."""
        # First set a setting value
        with app.app_context():
            Settings.set_setting('pgadmin_url', 'http://test:5050')

        csrf = get_csrf_token(auth_client, '/settings/')
        auth_client.post('/settings/reset-database', data={
            'csrf_token': csrf,
        }, follow_redirects=True)

        # Settings should still be there (the reset SQL does not include settings table)
        with app.app_context():
            url = Settings.get_setting('pgadmin_url')
            assert url == 'http://test:5050'


class TestSettingsSeedDataIdempotency:
    """Tests that seed data creation is idempotent or handles re-runs gracefully."""

    def test_create_default_categories_twice(self, auth_client, app, db):
        """Creating default categories twice does not cause errors."""
        csrf = get_csrf_token(auth_client, '/settings/')
        auth_client.post('/settings/create-default-categories', data={
            'csrf_token': csrf,
        }, follow_redirects=True)

        with app.app_context():
            first_count = Category.query.count()

        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/create-default-categories', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        # Should either succeed (idempotent) or show error (no crash)
        assert response.status_code == 200

    def test_create_default_tags_twice(self, auth_client, app, db):
        """Creating default tags twice does not cause errors."""
        csrf = get_csrf_token(auth_client, '/settings/')
        auth_client.post('/settings/create-default-tags', data={
            'csrf_token': csrf,
        }, follow_redirects=True)

        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/create-default-tags', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_create_default_investment_types_twice(self, auth_client, app, db):
        """Creating default investment types twice does not cause errors."""
        csrf = get_csrf_token(auth_client, '/settings/')
        auth_client.post('/settings/create-default-investment-types', data={
            'csrf_token': csrf,
        }, follow_redirects=True)

        csrf = get_csrf_token(auth_client, '/settings/')
        response = auth_client.post('/settings/create-default-investment-types', data={
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
