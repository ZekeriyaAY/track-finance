"""Tests for authentication and authorization security.

Verifies that unauthenticated access is blocked, open redirect attacks are
prevented, and passwords are stored securely as hashes.
"""
import pytest
from models.user import User
from models import db as _db
from tests.conftest import get_csrf_token


@pytest.mark.security
class TestUnauthenticatedAccessBlocked:
    """Unauthenticated requests to protected routes must redirect to login."""

    @pytest.mark.parametrize("url", [
        '/cashflow/',
        '/cashflow/dashboard',
        '/cashflow/add',
        '/cashflow/import',
        '/categories/',
        '/categories/add',
        '/tags/',
        '/tags/add',
        '/investments/',
        '/investments/add',
        '/investment-types/',
        '/investment-types/add',
        '/settings/',
        '/auth/account',
    ])
    def test_get_routes_redirect_to_login(self, client, admin_user, url):
        """GET on protected routes without auth should redirect to login."""
        response = client.get(url)
        assert response.status_code == 302
        location = response.headers.get('Location', '')
        assert '/auth/login' in location

    @pytest.mark.parametrize("url", [
        '/cashflow/add',
        '/cashflow/sync',
        '/cashflow/bulk-edit',
        '/categories/add',
        '/tags/add',
        '/investments/add',
        '/investment-types/add',
        '/settings/update-pgadmin-url',
        '/settings/create-dummy-data',
        '/settings/create-default-categories',
        '/settings/create-default-tags',
        '/settings/create-default-investment-types',
        '/settings/reset-database',
    ])
    def test_post_routes_redirect_to_login(self, client, admin_user, url):
        """POST on protected routes without auth should redirect to login."""
        response = client.post(url, data={'csrf_token': 'irrelevant'})
        # Should redirect to login (302) or fail CSRF before that (400).
        # Either way, the action must not succeed.
        assert response.status_code in (302, 400)
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            assert '/auth/login' in location

    def test_edit_cashflow_unauthenticated(self, client, admin_user, sample_transaction):
        """POST /cashflow/edit/<id> without auth redirects to login."""
        response = client.post(f'/cashflow/edit/{sample_transaction.id}', data={
            'date': '2024-01-15',
            'amount': '999',
            'type': 'expense',
            'category_id': str(sample_transaction.category_id),
            'description': 'Hacked',
        })
        assert response.status_code in (302, 400)
        if response.status_code == 302:
            assert '/auth/login' in response.headers.get('Location', '')

    def test_delete_cashflow_unauthenticated(self, client, admin_user, sample_transaction):
        """POST /cashflow/delete/<id> without auth redirects to login."""
        response = client.post(f'/cashflow/delete/{sample_transaction.id}')
        assert response.status_code in (302, 400)
        if response.status_code == 302:
            assert '/auth/login' in response.headers.get('Location', '')


@pytest.mark.security
class TestOpenRedirectPrevention:
    """Login next parameter must not allow redirects to external domains."""

    def test_open_redirect_double_slash_blocked(self, client, admin_user):
        """next=//evil.com must NOT redirect to external domain after login."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login?next=//evil.com', data={
            'username': 'admin',
            'password': 'testpassword123',
            'csrf_token': csrf,
        })
        assert response.status_code == 302
        location = response.headers.get('Location', '')
        # Must not redirect to //evil.com
        assert '//evil.com' not in location
        # Should redirect to internal default page
        assert '/cashflow' in location or location.endswith('/')

    def test_open_redirect_protocol_scheme_blocked(self, client, admin_user):
        """next=http://evil.com must NOT redirect externally."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login?next=http://evil.com', data={
            'username': 'admin',
            'password': 'testpassword123',
            'csrf_token': csrf,
        })
        assert response.status_code == 302
        location = response.headers.get('Location', '')
        assert 'evil.com' not in location

    def test_open_redirect_https_scheme_blocked(self, client, admin_user):
        """next=https://evil.com must NOT redirect externally."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login?next=https://evil.com', data={
            'username': 'admin',
            'password': 'testpassword123',
            'csrf_token': csrf,
        })
        assert response.status_code == 302
        location = response.headers.get('Location', '')
        assert 'evil.com' not in location

    def test_valid_relative_redirect_works(self, client, admin_user):
        """next=/cashflow/ should work correctly as a valid internal redirect."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login?next=/cashflow/', data={
            'username': 'admin',
            'password': 'testpassword123',
            'csrf_token': csrf,
        })
        assert response.status_code == 302
        location = response.headers.get('Location', '')
        assert '/cashflow/' in location

    def test_valid_relative_redirect_settings(self, client, admin_user):
        """next=/settings/ should redirect to settings after login."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login?next=/settings/', data={
            'username': 'admin',
            'password': 'testpassword123',
            'csrf_token': csrf,
        })
        assert response.status_code == 302
        location = response.headers.get('Location', '')
        assert '/settings/' in location

    def test_no_next_param_redirects_to_default(self, client, admin_user):
        """Login without next param should redirect to default cashflow page."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'testpassword123',
            'csrf_token': csrf,
        })
        assert response.status_code == 302
        location = response.headers.get('Location', '')
        assert '/cashflow' in location

    def test_backslash_double_redirect_blocked(self, client, admin_user):
        r"""next=\/evil.com should not be treated as protocol-relative."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login?next=%5C/evil.com', data={
            'username': 'admin',
            'password': 'testpassword123',
            'csrf_token': csrf,
        })
        assert response.status_code == 302
        location = response.headers.get('Location', '')
        # Should not redirect to evil.com
        assert 'evil.com' not in location or '/cashflow' in location


@pytest.mark.security
class TestPasswordSecurity:
    """Passwords must be stored as hashes, not plaintext."""

    def test_password_is_hashed(self, app, db, admin_user):
        """User password_hash should not equal the plaintext password."""
        with app.app_context():
            user = User.query.filter_by(username='admin').first()
            assert user is not None
            assert user.password_hash != 'testpassword123'
            assert len(user.password_hash) > 20  # Hash is substantially longer

    def test_password_hash_starts_with_hash_prefix(self, app, db, admin_user):
        """Werkzeug password hashes have a recognizable format."""
        with app.app_context():
            user = User.query.filter_by(username='admin').first()
            # Werkzeug hashes typically start with method identifier
            # e.g., "scrypt:", "pbkdf2:sha256:", etc.
            assert ':' in user.password_hash

    def test_password_verification_works(self, app, db, admin_user):
        """check_password returns True for correct password, False for wrong."""
        with app.app_context():
            user = User.query.filter_by(username='admin').first()
            assert user.check_password('testpassword123') is True
            assert user.check_password('wrongpassword') is False

    def test_different_passwords_produce_different_hashes(self, app, db):
        """Two users with different passwords should have different hashes."""
        with app.app_context():
            user1 = User(username='user1')
            user1.set_password('password_one')
            user2 = User(username='user2')
            user2.set_password('password_two')
            assert user1.password_hash != user2.password_hash

    def test_same_password_produces_different_hashes(self, app, db):
        """Same password hashed twice should produce different hashes (salt)."""
        with app.app_context():
            user1 = User(username='user_a')
            user1.set_password('samepassword')
            user2 = User(username='user_b')
            user2.set_password('samepassword')
            # Salted hashing means same password -> different hash
            assert user1.password_hash != user2.password_hash


@pytest.mark.security
class TestLoginBehavior:
    """Login edge cases and error handling."""

    def test_invalid_credentials_rejected(self, client, admin_user):
        """Login with wrong password shows error, does not authenticate."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'wrongpassword',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_nonexistent_user_rejected(self, client, admin_user):
        """Login with non-existent username shows error."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login', data={
            'username': 'nonexistent_user',
            'password': 'anypassword',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_empty_credentials_rejected(self, client, admin_user):
        """Login with empty username and password shows error."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login', data={
            'username': '',
            'password': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_authenticated_user_redirected_from_login(self, auth_client):
        """Already authenticated user visiting login page gets redirected."""
        response = auth_client.get('/auth/login')
        assert response.status_code == 302
        location = response.headers.get('Location', '')
        assert '/cashflow' in location
