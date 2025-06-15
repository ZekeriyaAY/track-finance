from datetime import datetime
from models.__init__ import db

class InvestmentTransaction(db.Model):
    """Yatırım işlemlerini (alım/satım) temsil eder."""
    __tablename__ = 'investment_transaction'
    id = db.Column(db.Integer, primary_key=True)
    investment_type_id = db.Column(db.Integer, db.ForeignKey('investment_type.id'), nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'buy' veya 'sell'
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, investment_type_id, transaction_date, transaction_type, price, quantity, description=None):
        self.investment_type_id = investment_type_id
        self.transaction_date = transaction_date
        self.transaction_type = transaction_type
        self.price = price
        self.quantity = quantity
        self.total_amount = price * quantity
        self.description = description 