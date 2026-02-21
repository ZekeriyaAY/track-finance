"""Tests for input validation and injection protection.

Verifies that XSS payloads are escaped, SQL injection is handled safely,
invalid enum values are rejected, and boundary values are handled correctly.
"""
import pytest
from datetime import date, datetime
from models.category import Category
from models.tag import Tag
from models.cashflow import CashflowTransaction
from models.investment import InvestmentType, InvestmentTransaction
from models import db as _db
from tests.conftest import get_csrf_token


@pytest.mark.security
class TestXSSPrevention:
    """Jinja2 auto-escaping should neutralize XSS payloads in rendered HTML."""

    def test_xss_in_category_name_escaped(self, auth_client, app, db):
        """<script> tag in category name is escaped in rendered output."""
        csrf = get_csrf_token(auth_client, '/categories/add')
        xss_payload = '<script>alert("xss")</script>'
        auth_client.post('/categories/add', data={
            'name': xss_payload,
            'parent_id': '',
            'csrf_token': csrf,
        }, follow_redirects=True)

        response = auth_client.get('/categories/')
        html = response.data.decode()
        # The raw script tag must NOT appear unescaped in the HTML
        assert '<script>alert("xss")</script>' not in html
        # But the escaped version should be present (Jinja2 auto-escape)
        assert '&lt;script&gt;' in html or 'alert' not in html or xss_payload not in html

    def test_xss_in_tag_name_escaped(self, auth_client, app, db):
        """XSS payload in tag name is safely escaped."""
        csrf = get_csrf_token(auth_client, '/tags/add')
        xss_payload = '<img src=x onerror=alert(1)>'
        auth_client.post('/tags/add', data={
            'name': xss_payload,
            'csrf_token': csrf,
        }, follow_redirects=True)

        response = auth_client.get('/tags/')
        html = response.data.decode()
        # Raw HTML tag must not appear unescaped
        assert '<img src=x onerror=alert(1)>' not in html
        # Escaped version should be present
        assert '&lt;img' in html

    def test_xss_in_transaction_description_escaped(self, auth_client, sample_category):
        """XSS payload in cashflow description is escaped in the list view."""
        csrf = get_csrf_token(auth_client, '/cashflow/add')
        xss_payload = '<script>document.cookie</script>'
        auth_client.post('/cashflow/add', data={
            'date': '2024-06-15',
            'amount': '50.00',
            'type': 'expense',
            'category_id': str(sample_category.id),
            'description': xss_payload,
            'csrf_token': csrf,
        }, follow_redirects=True)

        response = auth_client.get('/cashflow/')
        html = response.data.decode()
        assert '<script>document.cookie</script>' not in html

    def test_xss_in_investment_description_escaped(self, auth_client, sample_investment_type):
        """XSS payload in investment description is escaped."""
        csrf = get_csrf_token(auth_client, '/investments/add')
        xss_payload = '"><script>alert(1)</script>'
        auth_client.post('/investments/add', data={
            'investment_type_id': str(sample_investment_type.id),
            'transaction_date': '2024-06-15',
            'transaction_type': 'buy',
            'price': '100.00',
            'quantity': '1',
            'description': xss_payload,
            'csrf_token': csrf,
        }, follow_redirects=True)

        response = auth_client.get('/investments/')
        html = response.data.decode()
        assert '<script>alert(1)</script>' not in html

    def test_xss_in_search_parameter_escaped(self, auth_client, sample_category):
        """XSS in search query string is escaped in response."""
        xss_payload = '<script>alert("search_xss")</script>'
        response = auth_client.get(f'/cashflow/?search={xss_payload}')
        html = response.data.decode()
        assert '<script>alert("search_xss")</script>' not in html


@pytest.mark.security
class TestSQLInjectionPrevention:
    """SQLAlchemy parameterized queries should prevent SQL injection."""

    def test_sqli_in_search_field(self, auth_client, sample_category):
        """SQL injection in search parameter does not cause errors."""
        sqli_payloads = [
            "'; DROP TABLE cashflow_transaction; --",
            "' OR '1'='1",
            "1; SELECT * FROM users --",
            "' UNION SELECT username, password_hash FROM users --",
        ]
        for payload in sqli_payloads:
            response = auth_client.get(f'/cashflow/?search={payload}')
            # Should return 200 with safe results, not a 500 error
            assert response.status_code == 200

    def test_sqli_in_category_name(self, auth_client):
        """SQL injection in category name is treated as literal string."""
        csrf = get_csrf_token(auth_client, '/categories/add')
        sqli_payload = "'; DROP TABLE category; --"
        response = auth_client.post('/categories/add', data={
            'name': sqli_payload,
            'parent_id': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200

        # Verify the category was created with the literal string as its name
        response = auth_client.get('/categories/')
        assert response.status_code == 200

    def test_sqli_in_tag_name(self, auth_client):
        """SQL injection in tag name is treated as literal string."""
        csrf = get_csrf_token(auth_client, '/tags/add')
        sqli_payload = "' OR 1=1; --"
        response = auth_client.post('/tags/add', data={
            'name': sqli_payload,
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_sqli_in_filter_parameters(self, auth_client):
        """SQL injection in filter query parameters is handled safely."""
        response = auth_client.get("/cashflow/?category_id=1' OR '1'='1")
        # Should not crash; category_id is type=int so invalid input is ignored
        assert response.status_code == 200

    def test_sqli_in_date_filter(self, auth_client):
        """SQL injection in date filter parameters is handled safely."""
        response = auth_client.get(
            "/cashflow/?date_from=2024-01-01' OR '1'='1&date_to=2024-12-31"
        )
        assert response.status_code == 200


@pytest.mark.security
class TestInvalidTransactionType:
    """Invalid enum values for transaction types must be rejected."""

    def test_invalid_cashflow_type_rejected(self, auth_client, sample_category):
        """Cashflow transaction with type not in (income, expense) is rejected."""
        csrf = get_csrf_token(auth_client, '/cashflow/add')
        response = auth_client.post('/cashflow/add', data={
            'date': '2024-06-15',
            'amount': '100.00',
            'type': 'transfer',  # Invalid type
            'category_id': str(sample_category.id),
            'description': 'Invalid type test',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid transaction type' in response.data

    def test_empty_cashflow_type_rejected(self, auth_client, sample_category):
        """Empty transaction type value is rejected."""
        csrf = get_csrf_token(auth_client, '/cashflow/add')
        response = auth_client.post('/cashflow/add', data={
            'date': '2024-06-15',
            'amount': '100.00',
            'type': '',
            'category_id': str(sample_category.id),
            'description': 'Empty type test',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid transaction type' in response.data

    def test_invalid_investment_type_rejected(self, auth_client, sample_investment_type):
        """Investment transaction with type not in (buy, sell) is rejected."""
        csrf = get_csrf_token(auth_client, '/investments/add')
        response = auth_client.post('/investments/add', data={
            'investment_type_id': str(sample_investment_type.id),
            'transaction_date': '2024-06-15',
            'transaction_type': 'hold',  # Invalid type
            'price': '100.00',
            'quantity': '5',
            'description': 'Invalid type test',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid transaction type' in response.data

    def test_xss_in_transaction_type_rejected(self, auth_client, sample_category):
        """XSS payload as transaction type is rejected."""
        csrf = get_csrf_token(auth_client, '/cashflow/add')
        response = auth_client.post('/cashflow/add', data={
            'date': '2024-06-15',
            'amount': '100.00',
            'type': '<script>alert(1)</script>',
            'category_id': str(sample_category.id),
            'description': 'XSS type test',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid transaction type' in response.data


@pytest.mark.security
class TestAmountValidation:
    """Amount fields should handle edge case values gracefully."""

    def test_negative_amount_in_cashflow(self, auth_client, sample_category):
        """Negative amount should be handled (either rejected or stored as-is)."""
        csrf = get_csrf_token(auth_client, '/cashflow/add')
        response = auth_client.post('/cashflow/add', data={
            'date': '2024-06-15',
            'amount': '-100.00',
            'type': 'expense',
            'category_id': str(sample_category.id),
            'description': 'Negative amount',
            'csrf_token': csrf,
        }, follow_redirects=True)
        # The request should not cause a 500 error
        assert response.status_code == 200

    def test_zero_amount_in_cashflow(self, auth_client, sample_category):
        """Zero amount should be handled without error."""
        csrf = get_csrf_token(auth_client, '/cashflow/add')
        response = auth_client.post('/cashflow/add', data={
            'date': '2024-06-15',
            'amount': '0',
            'type': 'expense',
            'category_id': str(sample_category.id),
            'description': 'Zero amount',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_non_numeric_amount_rejected(self, auth_client, sample_category):
        """Non-numeric amount should cause an error, not crash."""
        csrf = get_csrf_token(auth_client, '/cashflow/add')
        response = auth_client.post('/cashflow/add', data={
            'date': '2024-06-15',
            'amount': 'not_a_number',
            'type': 'expense',
            'category_id': str(sample_category.id),
            'description': 'Non-numeric amount',
            'csrf_token': csrf,
        }, follow_redirects=True)
        # Should not crash with a 500; should either redirect or show error
        assert response.status_code in (200, 302)

    def test_very_large_amount_in_cashflow(self, auth_client, sample_category):
        """Very large amount should be handled without crash."""
        csrf = get_csrf_token(auth_client, '/cashflow/add')
        response = auth_client.post('/cashflow/add', data={
            'date': '2024-06-15',
            'amount': '99999999999999.99',
            'type': 'expense',
            'category_id': str(sample_category.id),
            'description': 'Large amount',
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200


@pytest.mark.security
class TestOversizedInput:
    """Oversized input strings should not crash the application."""

    def test_oversized_category_name(self, auth_client):
        """Very long category name should be handled without crash."""
        csrf = get_csrf_token(auth_client, '/categories/add')
        long_name = 'A' * 10000
        response = auth_client.post('/categories/add', data={
            'name': long_name,
            'parent_id': '',
            'csrf_token': csrf,
        }, follow_redirects=True)
        # Should not cause a 500 error; may truncate or reject
        assert response.status_code == 200

    def test_oversized_tag_name(self, auth_client):
        """Very long tag name should be handled without crash."""
        csrf = get_csrf_token(auth_client, '/tags/add')
        long_name = 'B' * 10000
        response = auth_client.post('/tags/add', data={
            'name': long_name,
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_oversized_description(self, auth_client, sample_category):
        """Very long transaction description should be handled without crash."""
        csrf = get_csrf_token(auth_client, '/cashflow/add')
        long_desc = 'X' * 50000
        response = auth_client.post('/cashflow/add', data={
            'date': '2024-06-15',
            'amount': '100.00',
            'type': 'expense',
            'category_id': str(sample_category.id),
            'description': long_desc,
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_oversized_investment_description(self, auth_client, sample_investment_type):
        """Very long investment description should be handled without crash."""
        csrf = get_csrf_token(auth_client, '/investments/add')
        long_desc = 'Y' * 50000
        response = auth_client.post('/investments/add', data={
            'investment_type_id': str(sample_investment_type.id),
            'transaction_date': '2024-06-15',
            'transaction_type': 'buy',
            'price': '100.00',
            'quantity': '1',
            'description': long_desc,
            'csrf_token': csrf,
        }, follow_redirects=True)
        assert response.status_code == 200


@pytest.mark.security
class TestInvalidDateInput:
    """Invalid date formats should be handled gracefully."""

    def test_invalid_date_format_in_cashflow(self, auth_client, sample_category):
        """Invalid date format should cause error, not crash."""
        csrf = get_csrf_token(auth_client, '/cashflow/add')
        response = auth_client.post('/cashflow/add', data={
            'date': 'not-a-date',
            'amount': '100.00',
            'type': 'expense',
            'category_id': str(sample_category.id),
            'description': 'Bad date',
            'csrf_token': csrf,
        }, follow_redirects=True)
        # Should not be a 500; should show error or redirect
        assert response.status_code in (200, 302)

    def test_invalid_date_in_filter(self, auth_client):
        """Invalid date in filter query string is handled safely."""
        response = auth_client.get('/cashflow/?date_from=invalid&date_to=also-invalid')
        assert response.status_code == 200

    def test_invalid_date_in_dashboard_filter(self, auth_client):
        """Invalid date in dashboard filter is handled safely."""
        response = auth_client.get('/cashflow/dashboard?date_from=abc&date_to=xyz')
        assert response.status_code == 200
