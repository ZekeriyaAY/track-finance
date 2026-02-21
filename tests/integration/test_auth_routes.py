"""Integration tests for authentication routes (/auth)."""
import pytest
from tests.conftest import get_csrf_token
from models.user import User


pytestmark = pytest.mark.integration


class TestLoginRoute:
    """Tests for GET/POST /auth/login."""

    def test_login_page_renders(self, client):
        """GET /auth/login returns the login form."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'Login' in response.data

    def test_login_page_contains_csrf_token(self, client):
        """Login page includes a CSRF token in the form."""
        response = client.get('/auth/login')
        assert b'csrf_token' in response.data

    def test_login_valid_credentials(self, client, admin_user):
        """POST /auth/login with valid credentials redirects to cashflow index."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'testpassword123',
            'csrf_token': csrf,
        }, follow_redirects=False)
        # Should redirect (302) to cashflow index
        assert response.status_code == 302
        assert '/cashflow' in response.headers.get('Location', '')

    def test_login_valid_credentials_follow_redirect(self, client, admin_user):
        """POST /auth/login with valid credentials loads the cashflow page."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'testpassword123',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_invalid_password(self, client, admin_user):
        """POST /auth/login with wrong password shows error flash."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'wrongpassword',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_login_invalid_username(self, client, admin_user):
        """POST /auth/login with nonexistent username shows error flash."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'testpassword123',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_login_empty_fields(self, client, admin_user):
        """POST /auth/login with empty fields shows error flash."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login', data={
            'username': '',
            'password': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_login_already_authenticated_redirects(self, auth_client):
        """GET /auth/login when already logged in redirects to cashflow index."""
        response = auth_client.get('/auth/login', follow_redirects=False)
        assert response.status_code == 302
        assert '/cashflow' in response.headers.get('Location', '')

    def test_login_with_remember_me(self, client, admin_user):
        """POST /auth/login with remember checkbox sets session correctly."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'testpassword123',
            'remember': 'on',
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302

    def test_login_with_next_redirect(self, client, admin_user):
        """POST /auth/login with next param redirects to that page after login."""
        csrf = get_csrf_token(client, '/auth/login')
        response = client.post('/auth/login?next=/settings/', data={
            'username': 'admin',
            'password': 'testpassword123',
            'csrf_token': csrf,
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/settings/' in response.headers.get('Location', '')


class TestLogoutRoute:
    """Tests for GET /auth/logout."""

    def test_logout_redirects_to_login(self, auth_client):
        """GET /auth/logout logs out and redirects to login page."""
        response = auth_client.get('/auth/logout', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers.get('Location', '')

    def test_logout_shows_flash_message(self, auth_client):
        """GET /auth/logout shows logout success flash."""
        response = auth_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'You have been logged out' in response.data

    def test_logout_prevents_access_after(self, auth_client):
        """After logout, accessing protected pages redirects to login."""
        auth_client.get('/auth/logout')
        response = auth_client.get('/cashflow/', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers.get('Location', '')

    def test_logout_requires_authentication(self, client, admin_user):
        """GET /auth/logout when not logged in redirects to login."""
        response = client.get('/auth/logout', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers.get('Location', '')


class TestAccountRoute:
    """Tests for GET /auth/account."""

    def test_account_page_renders(self, auth_client):
        """GET /auth/account returns the account settings page."""
        response = auth_client.get('/auth/account')
        assert response.status_code == 200
        assert b'csrf_token' in response.data

    def test_account_requires_authentication(self, client, admin_user):
        """GET /auth/account redirects to login when not authenticated."""
        response = client.get('/auth/account', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers.get('Location', '')


class TestChangePasswordRoute:
    """Tests for POST /auth/change-password."""

    def test_change_password_success(self, auth_client, app):
        """POST /auth/change-password with valid data updates the password."""
        csrf = get_csrf_token(auth_client, '/auth/account')
        response = auth_client.post('/auth/change-password', data={
            'current_password': 'testpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Password changed successfully' in response.data

        # Verify the new password works
        with app.app_context():
            user = User.query.filter_by(username='admin').first()
            assert user.check_password('newpassword456')

    def test_change_password_wrong_current(self, auth_client):
        """POST /auth/change-password with wrong current password shows error."""
        csrf = get_csrf_token(auth_client, '/auth/account')
        response = auth_client.post('/auth/change-password', data={
            'current_password': 'wrongpassword',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Current password is incorrect' in response.data

    def test_change_password_too_short(self, auth_client):
        """POST /auth/change-password with short new password shows error."""
        csrf = get_csrf_token(auth_client, '/auth/account')
        response = auth_client.post('/auth/change-password', data={
            'current_password': 'testpassword123',
            'new_password': 'abc',
            'confirm_password': 'abc',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'at least 6 characters' in response.data

    def test_change_password_mismatch(self, auth_client):
        """POST /auth/change-password with non-matching passwords shows error."""
        csrf = get_csrf_token(auth_client, '/auth/account')
        response = auth_client.post('/auth/change-password', data={
            'current_password': 'testpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'differentpassword',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'do not match' in response.data

    def test_change_password_exactly_6_chars(self, auth_client):
        """POST /auth/change-password with exactly 6 character password succeeds."""
        csrf = get_csrf_token(auth_client, '/auth/account')
        response = auth_client.post('/auth/change-password', data={
            'current_password': 'testpassword123',
            'new_password': '123456',
            'confirm_password': '123456',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Password changed successfully' in response.data


class TestChangeUsernameRoute:
    """Tests for POST /auth/change-username."""

    def test_change_username_success(self, auth_client, app):
        """POST /auth/change-username with valid data updates the username."""
        csrf = get_csrf_token(auth_client, '/auth/account')
        response = auth_client.post('/auth/change-username', data={
            'new_username': 'newadmin',
            'password': 'testpassword123',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Username changed successfully' in response.data

        # Verify the username was updated in the database
        with app.app_context():
            user = User.query.first()
            assert user.username == 'newadmin'

    def test_change_username_wrong_password(self, auth_client):
        """POST /auth/change-username with wrong password shows error."""
        csrf = get_csrf_token(auth_client, '/auth/account')
        response = auth_client.post('/auth/change-username', data={
            'new_username': 'newadmin',
            'password': 'wrongpassword',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Password is incorrect' in response.data

    def test_change_username_too_short(self, auth_client):
        """POST /auth/change-username with short username shows error."""
        csrf = get_csrf_token(auth_client, '/auth/account')
        response = auth_client.post('/auth/change-username', data={
            'new_username': 'ab',
            'password': 'testpassword123',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'at least 3 characters' in response.data

    def test_change_username_same_as_current(self, auth_client):
        """POST /auth/change-username with same username shows error."""
        csrf = get_csrf_token(auth_client, '/auth/account')
        response = auth_client.post('/auth/change-username', data={
            'new_username': 'admin',
            'password': 'testpassword123',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'same as current' in response.data

    def test_change_username_exactly_3_chars(self, auth_client):
        """POST /auth/change-username with exactly 3 character username succeeds."""
        csrf = get_csrf_token(auth_client, '/auth/account')
        response = auth_client.post('/auth/change-username', data={
            'new_username': 'abc',
            'password': 'testpassword123',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Username changed successfully' in response.data


class TestAuthRequirement:
    """Tests for global authentication requirement."""

    def test_unauthenticated_access_redirects_to_login(self, client, admin_user):
        """Unauthenticated access to protected routes redirects to login."""
        protected_urls = [
            '/cashflow/',
            '/cashflow/dashboard',
            '/categories/',
            '/tags/',
            '/investments/',
            '/investment-types/',
            '/settings/',
        ]
        for url in protected_urls:
            response = client.get(url, follow_redirects=False)
            assert response.status_code == 302, f"Expected redirect for {url}"
            assert '/auth/login' in response.headers.get('Location', ''), \
                f"Expected redirect to login for {url}"

    def test_health_check_accessible_without_auth(self, client, admin_user):
        """Health check endpoint is accessible without authentication."""
        response = client.get('/health')
        assert response.status_code == 200

    def test_static_files_accessible_without_auth(self, client, admin_user):
        """Static file endpoint does not require authentication."""
        # The static endpoint exists but specific files may or may not exist;
        # the important thing is that it does not redirect to login.
        response = client.get('/static/css/style.css')
        # Either 200 (file found) or 404, but NOT a redirect to login
        assert response.status_code in (200, 404)
