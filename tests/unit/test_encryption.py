"""Unit tests for Fernet encryption utilities."""
import pytest

from utils.encryption import encrypt_value, decrypt_value, _get_fernet_key


@pytest.mark.unit
class TestEncryption:
    """Tests for encrypt_value / decrypt_value using Fernet derived from SECRET_KEY."""

    def test_roundtrip(self, app):
        """Encrypting then decrypting returns the original plaintext."""
        with app.app_context():
            plaintext = 'my-secret-client-id'
            ciphertext = encrypt_value(plaintext)
            assert ciphertext is not None
            assert ciphertext != plaintext
            assert decrypt_value(ciphertext) == plaintext

    def test_roundtrip_unicode(self, app):
        """Unicode strings survive encrypt/decrypt roundtrip."""
        with app.app_context():
            plaintext = 'Türkçe şifre: güçlü!'
            ciphertext = encrypt_value(plaintext)
            assert decrypt_value(ciphertext) == plaintext

    def test_roundtrip_long_string(self, app):
        """Long strings survive encrypt/decrypt roundtrip."""
        with app.app_context():
            plaintext = 'x' * 10000
            ciphertext = encrypt_value(plaintext)
            assert decrypt_value(ciphertext) == plaintext

    def test_none_input_encrypt(self, app):
        """encrypt_value returns None for None input."""
        with app.app_context():
            assert encrypt_value(None) is None

    def test_none_input_decrypt(self, app):
        """decrypt_value returns None for None input."""
        with app.app_context():
            assert decrypt_value(None) is None

    def test_empty_string_encrypt(self, app):
        """encrypt_value returns None for empty string input."""
        with app.app_context():
            assert encrypt_value('') is None

    def test_empty_string_decrypt(self, app):
        """decrypt_value returns None for empty string input."""
        with app.app_context():
            assert decrypt_value('') is None

    def test_ciphertext_is_different_from_plaintext(self, app):
        """Ciphertext should not equal plaintext."""
        with app.app_context():
            plaintext = 'hello-world'
            ciphertext = encrypt_value(plaintext)
            assert ciphertext != plaintext

    def test_different_plaintexts_produce_different_ciphertexts(self, app):
        """Different inputs should not produce the same ciphertext."""
        with app.app_context():
            c1 = encrypt_value('value-one')
            c2 = encrypt_value('value-two')
            assert c1 != c2

    def test_same_plaintext_produces_different_ciphertext_each_call(self, app):
        """Fernet uses a nonce, so identical plaintexts yield different ciphertexts."""
        with app.app_context():
            c1 = encrypt_value('same-value')
            c2 = encrypt_value('same-value')
            # Fernet includes a timestamp/nonce, ciphertexts should differ
            assert c1 != c2
            # But both decrypt to the same value
            assert decrypt_value(c1) == decrypt_value(c2) == 'same-value'

    def test_fernet_key_derived_from_secret_key(self, app):
        """_get_fernet_key produces a consistent key for the same SECRET_KEY."""
        with app.app_context():
            key1 = _get_fernet_key()
            key2 = _get_fernet_key()
            assert key1 == key2

    def test_different_secret_key_produces_different_fernet_key(self, app):
        """A different SECRET_KEY yields a different Fernet key."""
        with app.app_context():
            key_original = _get_fernet_key()

        # Temporarily change SECRET_KEY
        original_secret = app.config['SECRET_KEY']
        app.config['SECRET_KEY'] = 'completely-different-secret-key-value'
        try:
            with app.app_context():
                key_different = _get_fernet_key()
            assert key_original != key_different
        finally:
            app.config['SECRET_KEY'] = original_secret

    def test_different_secret_key_cannot_decrypt(self, app):
        """Ciphertext from one SECRET_KEY cannot be decrypted with a different one."""
        with app.app_context():
            ciphertext = encrypt_value('secret-data')

        original_secret = app.config['SECRET_KEY']
        app.config['SECRET_KEY'] = 'another-totally-different-key'
        try:
            with app.app_context():
                # Fernet decrypt with wrong key should fail
                with pytest.raises(Exception):
                    decrypt_value(ciphertext)
        finally:
            app.config['SECRET_KEY'] = original_secret
