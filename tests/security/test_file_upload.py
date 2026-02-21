"""Tests for file upload security.

Verifies that only allowed file extensions are accepted, empty files are handled,
and invalid upload scenarios do not crash the application.
"""
import pytest
from io import BytesIO
from tests.conftest import get_csrf_token


@pytest.mark.security
class TestFileExtensionValidation:
    """Only xlsx, xls, csv extensions should be accepted for import."""

    def test_xlsx_extension_accepted(self, auth_client):
        """A .xlsx file should pass the extension check (may fail on content parsing)."""
        csrf = get_csrf_token(auth_client, '/cashflow/import')
        # Create a fake xlsx file (will fail during actual parsing, but should pass
        # the extension check and not return an extension error)
        fake_file = BytesIO(b'\x00\x01\x02\x03fake xlsx content')
        response = auth_client.post('/cashflow/import', data={
            'excel_file': (fake_file, 'transactions.xlsx'),
            'bank_code': 'yapikredi',
            'csrf_token': csrf,
        }, content_type='multipart/form-data', follow_redirects=True)
        html = response.data.decode()
        # Should NOT see the extension error; may see parsing error instead
        assert 'Only Excel files' not in html

    def test_xls_extension_accepted(self, auth_client):
        """A .xls file should pass the extension check."""
        csrf = get_csrf_token(auth_client, '/cashflow/import')
        fake_file = BytesIO(b'\x00\x01\x02\x03fake xls content')
        response = auth_client.post('/cashflow/import', data={
            'excel_file': (fake_file, 'transactions.xls'),
            'bank_code': 'yapikredi',
            'csrf_token': csrf,
        }, content_type='multipart/form-data', follow_redirects=True)
        html = response.data.decode()
        assert 'Only Excel files' not in html

    def test_csv_extension_accepted(self, auth_client):
        """A .csv file should pass the extension check."""
        csrf = get_csrf_token(auth_client, '/cashflow/import')
        fake_file = BytesIO(b'date,amount,description\n2024-01-01,100,Test')
        response = auth_client.post('/cashflow/import', data={
            'excel_file': (fake_file, 'transactions.csv'),
            'bank_code': 'yapikredi',
            'csrf_token': csrf,
        }, content_type='multipart/form-data', follow_redirects=True)
        html = response.data.decode()
        assert 'Only Excel files' not in html

    def test_exe_extension_rejected(self, auth_client):
        """A .exe file must be rejected."""
        csrf = get_csrf_token(auth_client, '/cashflow/import')
        fake_file = BytesIO(b'MZ\x90\x00fake executable')
        response = auth_client.post('/cashflow/import', data={
            'excel_file': (fake_file, 'malware.exe'),
            'bank_code': 'yapikredi',
            'csrf_token': csrf,
        }, content_type='multipart/form-data', follow_redirects=True)
        html = response.data.decode()
        assert 'Only Excel files' in html

    def test_py_extension_rejected(self, auth_client):
        """A .py file must be rejected."""
        csrf = get_csrf_token(auth_client, '/cashflow/import')
        fake_file = BytesIO(b'import os; os.system("rm -rf /")')
        response = auth_client.post('/cashflow/import', data={
            'excel_file': (fake_file, 'script.py'),
            'bank_code': 'yapikredi',
            'csrf_token': csrf,
        }, content_type='multipart/form-data', follow_redirects=True)
        html = response.data.decode()
        assert 'Only Excel files' in html

    def test_php_extension_rejected(self, auth_client):
        """A .php file must be rejected."""
        csrf = get_csrf_token(auth_client, '/cashflow/import')
        fake_file = BytesIO(b'<?php echo shell_exec("whoami"); ?>')
        response = auth_client.post('/cashflow/import', data={
            'excel_file': (fake_file, 'shell.php'),
            'bank_code': 'yapikredi',
            'csrf_token': csrf,
        }, content_type='multipart/form-data', follow_redirects=True)
        html = response.data.decode()
        assert 'Only Excel files' in html

    def test_html_extension_rejected(self, auth_client):
        """A .html file must be rejected."""
        csrf = get_csrf_token(auth_client, '/cashflow/import')
        fake_file = BytesIO(b'<html><script>alert(1)</script></html>')
        response = auth_client.post('/cashflow/import', data={
            'excel_file': (fake_file, 'page.html'),
            'bank_code': 'yapikredi',
            'csrf_token': csrf,
        }, content_type='multipart/form-data', follow_redirects=True)
        html = response.data.decode()
        assert 'Only Excel files' in html

    def test_txt_extension_rejected(self, auth_client):
        """A .txt file must be rejected."""
        csrf = get_csrf_token(auth_client, '/cashflow/import')
        fake_file = BytesIO(b'just a text file')
        response = auth_client.post('/cashflow/import', data={
            'excel_file': (fake_file, 'data.txt'),
            'bank_code': 'yapikredi',
            'csrf_token': csrf,
        }, content_type='multipart/form-data', follow_redirects=True)
        html = response.data.decode()
        assert 'Only Excel files' in html

    def test_double_extension_rejected(self, auth_client):
        """A file with double extension like .xlsx.exe should be rejected."""
        csrf = get_csrf_token(auth_client, '/cashflow/import')
        fake_file = BytesIO(b'fake content')
        response = auth_client.post('/cashflow/import', data={
            'excel_file': (fake_file, 'data.xlsx.exe'),
            'bank_code': 'yapikredi',
            'csrf_token': csrf,
        }, content_type='multipart/form-data', follow_redirects=True)
        html = response.data.decode()
        # The allowed_file function checks the last extension after rsplit('.', 1)
        # so .xlsx.exe -> ext is 'exe' -> rejected
        assert 'Only Excel files' in html

    def test_no_extension_rejected(self, auth_client):
        """A file with no extension should be rejected."""
        csrf = get_csrf_token(auth_client, '/cashflow/import')
        fake_file = BytesIO(b'no extension file')
        response = auth_client.post('/cashflow/import', data={
            'excel_file': (fake_file, 'noextension'),
            'bank_code': 'yapikredi',
            'csrf_token': csrf,
        }, content_type='multipart/form-data', follow_redirects=True)
        html = response.data.decode()
        assert 'Only Excel files' in html


@pytest.mark.security
class TestEmptyFileHandling:
    """Empty or missing file submissions should be handled gracefully."""

    def test_no_file_selected(self, auth_client):
        """Submitting import form without selecting a file shows error."""
        csrf = get_csrf_token(auth_client, '/cashflow/import')
        response = auth_client.post('/cashflow/import', data={
            'bank_code': 'yapikredi',
            'csrf_token': csrf,
        }, content_type='multipart/form-data', follow_redirects=True)
        html = response.data.decode()
        assert 'Please select' in html

    def test_empty_filename(self, auth_client):
        """Submitting a file with empty filename shows error."""
        csrf = get_csrf_token(auth_client, '/cashflow/import')
        # Empty filename simulates browser sending no file selected
        fake_file = BytesIO(b'')
        response = auth_client.post('/cashflow/import', data={
            'excel_file': (fake_file, ''),
            'bank_code': 'yapikredi',
            'csrf_token': csrf,
        }, content_type='multipart/form-data', follow_redirects=True)
        html = response.data.decode()
        assert 'Please select' in html

    def test_empty_file_content(self, auth_client):
        """Submitting an empty xlsx file should not crash."""
        csrf = get_csrf_token(auth_client, '/cashflow/import')
        empty_file = BytesIO(b'')
        response = auth_client.post('/cashflow/import', data={
            'excel_file': (empty_file, 'empty.xlsx'),
            'bank_code': 'yapikredi',
            'csrf_token': csrf,
        }, content_type='multipart/form-data', follow_redirects=True)
        # Should not crash; should show some error about invalid content
        assert response.status_code == 200


@pytest.mark.security
class TestMissingBankCode:
    """Import requires a bank_code selection."""

    def test_no_bank_code_selected(self, auth_client):
        """Submitting import without bank selection shows error."""
        csrf = get_csrf_token(auth_client, '/cashflow/import')
        fake_file = BytesIO(b'fake content')
        response = auth_client.post('/cashflow/import', data={
            'excel_file': (fake_file, 'test.xlsx'),
            'bank_code': '',
            'csrf_token': csrf,
        }, content_type='multipart/form-data', follow_redirects=True)
        html = response.data.decode()
        assert 'Please select a bank' in html

    def test_missing_bank_code_field(self, auth_client):
        """Submitting import without bank_code field at all shows error."""
        csrf = get_csrf_token(auth_client, '/cashflow/import')
        fake_file = BytesIO(b'fake content')
        response = auth_client.post('/cashflow/import', data={
            'excel_file': (fake_file, 'test.xlsx'),
            'csrf_token': csrf,
        }, content_type='multipart/form-data', follow_redirects=True)
        html = response.data.decode()
        assert 'Please select a bank' in html


@pytest.mark.security
class TestFileUploadUnauthenticated:
    """File upload endpoints should require authentication."""

    def test_import_get_unauthenticated(self, client, admin_user):
        """GET /cashflow/import without auth redirects to login."""
        response = client.get('/cashflow/import')
        assert response.status_code == 302
        assert '/auth/login' in response.headers.get('Location', '')

    def test_import_post_unauthenticated(self, client, admin_user):
        """POST /cashflow/import without auth redirects to login or fails CSRF."""
        fake_file = BytesIO(b'fake content')
        response = client.post('/cashflow/import', data={
            'excel_file': (fake_file, 'test.xlsx'),
            'bank_code': 'yapikredi',
        }, content_type='multipart/form-data')
        assert response.status_code in (302, 400)
        if response.status_code == 302:
            assert '/auth/login' in response.headers.get('Location', '')
