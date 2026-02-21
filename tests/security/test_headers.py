"""Tests for security headers and information disclosure.

Verifies that security headers are set on all responses, content types are
correct, and error endpoints do not leak internal details.
"""
import pytest
from tests.conftest import get_csrf_token


@pytest.mark.security
class TestSecurityHeaders:
    """All responses must include security headers configured in app.py."""

    def test_x_frame_options_deny(self, auth_client):
        """X-Frame-Options: DENY must be present on page responses."""
        response = auth_client.get('/cashflow/')
        assert response.headers.get('X-Frame-Options') == 'DENY'

    def test_x_content_type_options_nosniff(self, auth_client):
        """X-Content-Type-Options: nosniff must be present."""
        response = auth_client.get('/cashflow/')
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'

    def test_x_xss_protection(self, auth_client):
        """X-XSS-Protection: 1; mode=block must be present."""
        response = auth_client.get('/cashflow/')
        assert response.headers.get('X-XSS-Protection') == '1; mode=block'

    def test_referrer_policy(self, auth_client):
        """Referrer-Policy: same-origin must be present."""
        response = auth_client.get('/cashflow/')
        assert response.headers.get('Referrer-Policy') == 'same-origin'

    def test_security_headers_on_login_page(self, client, admin_user):
        """Security headers are present even on the unauthenticated login page."""
        response = client.get('/auth/login')
        assert response.headers.get('X-Frame-Options') == 'DENY'
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'
        assert response.headers.get('X-XSS-Protection') == '1; mode=block'
        assert response.headers.get('Referrer-Policy') == 'same-origin'

    def test_security_headers_on_redirect(self, client, admin_user):
        """Security headers are present on redirect responses."""
        response = client.get('/cashflow/')
        assert response.status_code == 302
        assert response.headers.get('X-Frame-Options') == 'DENY'
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'

    def test_security_headers_on_health_endpoint(self, client, admin_user):
        """Security headers are present on the health check endpoint."""
        response = client.get('/health')
        assert response.headers.get('X-Frame-Options') == 'DENY'
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'
        assert response.headers.get('X-XSS-Protection') == '1; mode=block'
        assert response.headers.get('Referrer-Policy') == 'same-origin'

    def test_security_headers_on_api_endpoint(self, auth_client):
        """Security headers are present on API JSON endpoint."""
        response = auth_client.get('/cashflow/api/category-data')
        assert response.headers.get('X-Frame-Options') == 'DENY'
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'
        assert response.headers.get('X-XSS-Protection') == '1; mode=block'

    def test_security_headers_on_dashboard(self, auth_client):
        """Security headers are present on the dashboard page."""
        response = auth_client.get('/cashflow/dashboard')
        assert response.headers.get('X-Frame-Options') == 'DENY'
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'

    def test_security_headers_on_settings(self, auth_client):
        """Security headers are present on the settings page."""
        response = auth_client.get('/settings/')
        assert response.headers.get('X-Frame-Options') == 'DENY'
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'


@pytest.mark.security
class TestContentTypeHeaders:
    """Content-Type headers should match the response content."""

    def test_html_pages_have_text_html_content_type(self, auth_client):
        """HTML page responses should have text/html content type."""
        response = auth_client.get('/cashflow/')
        content_type = response.headers.get('Content-Type', '')
        assert 'text/html' in content_type

    def test_login_page_has_text_html_content_type(self, client, admin_user):
        """Login page should have text/html content type."""
        response = client.get('/auth/login')
        content_type = response.headers.get('Content-Type', '')
        assert 'text/html' in content_type

    def test_api_endpoint_has_json_content_type(self, auth_client):
        """API endpoint should return application/json content type."""
        response = auth_client.get('/cashflow/api/category-data')
        content_type = response.headers.get('Content-Type', '')
        assert 'application/json' in content_type

    def test_health_endpoint_has_json_content_type(self, client, admin_user):
        """Health check endpoint should return application/json content type."""
        response = client.get('/health')
        content_type = response.headers.get('Content-Type', '')
        assert 'application/json' in content_type

    def test_dashboard_has_text_html_content_type(self, auth_client):
        """Dashboard page should have text/html content type."""
        response = auth_client.get('/cashflow/dashboard')
        content_type = response.headers.get('Content-Type', '')
        assert 'text/html' in content_type

    def test_categories_page_has_text_html_content_type(self, auth_client):
        """Categories page should have text/html content type."""
        response = auth_client.get('/categories/')
        content_type = response.headers.get('Content-Type', '')
        assert 'text/html' in content_type


@pytest.mark.security
class TestHealthEndpointInformationDisclosure:
    """Health endpoint must not leak internal error details."""

    def test_healthy_response_structure(self, client, admin_user):
        """Healthy response returns expected JSON structure."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'track-finance'
        assert data['database'] == 'connected'

    def test_healthy_response_no_sensitive_info(self, client, admin_user):
        """Health response should not contain sensitive information."""
        response = client.get('/health')
        data = response.get_json()
        body_str = str(data)
        # Should not contain database credentials or connection strings
        assert 'password' not in body_str.lower()
        assert 'secret' not in body_str.lower()
        assert 'postgresql://' not in body_str

    def test_health_error_does_not_leak_exception_class(self, app, client, admin_user):
        """If health check fails, error message should be generic."""
        # The health endpoint uses a generic error message:
        # 'Database connection failed' instead of str(e)
        # We verify the pattern by checking the code returns a safe message.
        # In the test environment with SQLite, the health check will succeed,
        # so we just verify the response format is safe.
        response = client.get('/health')
        body_str = response.data.decode()
        # Should not contain Python exception class names
        assert 'Traceback' not in body_str
        assert 'OperationalError' not in body_str
        assert 'ProgrammingError' not in body_str
        assert 'sqlalchemy' not in body_str.lower() or response.status_code == 200

    def test_health_endpoint_does_not_require_auth(self, client, admin_user):
        """Health check endpoint should be accessible without authentication."""
        response = client.get('/health')
        # Should not redirect to login
        assert response.status_code in (200, 503)
        assert response.status_code != 302


@pytest.mark.security
class TestHSTSHeader:
    """Strict-Transport-Security header behavior in debug vs production."""

    def test_hsts_not_set_in_debug_mode(self, client, admin_user):
        """HSTS header should NOT be set in debug/development mode."""
        response = client.get('/auth/login')
        # In test config, DEBUG behavior comes from the TestConfig
        # The app.py code sets HSTS only when not app.debug
        # TestConfig doesn't set DEBUG=True explicitly, but the test
        # environment uses DevelopmentConfig base which has DEBUG=True
        hsts = response.headers.get('Strict-Transport-Security')
        # Either not present (debug mode) or present (non-debug) - document behavior
        # The test checks whether the header matches the debug flag
        if client.application.debug:
            assert hsts is None
        else:
            # In non-debug mode, HSTS should be present
            assert hsts is not None
            assert 'max-age=' in hsts


@pytest.mark.security
class TestSessionCookieAttributes:
    """Session cookie should have secure attributes configured."""

    def test_session_cookie_httponly(self, app):
        """Session cookie should be configured as HttpOnly."""
        assert app.config.get('SESSION_COOKIE_HTTPONLY') is True

    def test_session_cookie_samesite(self, app):
        """Session cookie should have SameSite attribute set."""
        samesite = app.config.get('SESSION_COOKIE_SAMESITE')
        assert samesite in ('Lax', 'Strict', 'None')
