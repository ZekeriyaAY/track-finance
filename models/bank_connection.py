from models.__init__ import db
from datetime import datetime
from utils.encryption import encrypt_value, decrypt_value


class BankConnection(db.Model):
    __tablename__ = 'bank_connection'

    id = db.Column(db.Integer, primary_key=True)
    bank_code = db.Column(db.String(50), nullable=False)
    bank_name = db.Column(db.String(100), nullable=False)
    client_id_encrypted = db.Column(db.Text, nullable=True)
    client_secret_encrypted = db.Column(db.Text, nullable=True)
    account_id = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    last_sync_at = db.Column(db.DateTime, nullable=True)
    last_sync_status = db.Column(db.String(20), nullable=True)
    last_sync_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transactions = db.relationship('CashflowTransaction', backref='bank_connection', lazy='dynamic')

    def set_client_id(self, plaintext):
        self.client_id_encrypted = encrypt_value(plaintext)

    def get_client_id(self):
        return decrypt_value(self.client_id_encrypted)

    def set_client_secret(self, plaintext):
        self.client_secret_encrypted = encrypt_value(plaintext)

    def get_client_secret(self):
        return decrypt_value(self.client_secret_encrypted)

    def __repr__(self):
        return f'<BankConnection {self.bank_name} ({self.bank_code})>'
