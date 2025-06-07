from models.__init__ import db
from models.transaction import Transaction # Import Transaction model

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    transactions = db.relationship('Transaction', secondary='transaction_tags', back_populates='tags')

    def get_income_count(self):
        return len([t for t in self.transactions if t.type == 'income'])

    def get_expense_count(self):
        return len([t for t in self.transactions if t.type == 'expense']) 