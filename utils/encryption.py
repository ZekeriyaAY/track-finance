import hashlib
import base64
from cryptography.fernet import Fernet
from flask import current_app


def _get_fernet_key():
    """Derive a Fernet key from Flask SECRET_KEY using SHA-256."""
    secret = current_app.config['SECRET_KEY']
    digest = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_value(plaintext):
    """Encrypt a plaintext string and return ciphertext."""
    if not plaintext:
        return None
    f = Fernet(_get_fernet_key())
    return f.encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext):
    """Decrypt a ciphertext string and return plaintext."""
    if not ciphertext:
        return None
    f = Fernet(_get_fernet_key())
    return f.decrypt(ciphertext.encode()).decode()
