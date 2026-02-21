from datetime import datetime, timezone
from models import db

class InvestmentType(db.Model):
    __tablename__ = 'investment_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True)  # For internal use (e.g., 'stock', 'crypto')
    icon = db.Column(db.String(50), nullable=False, default='fas fa-chart-pie')  # Font Awesome icon class
    color = db.Column(db.String(7), nullable=False, default='#3B82F6')  # Default blue color
    parent_id = db.Column(db.Integer, db.ForeignKey('investment_type.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    parent = db.relationship('InvestmentType', remote_side=[id], backref='children')
    investments = db.relationship('InvestmentTransaction', backref='investment_type', lazy=True)

    def __repr__(self):
        return f'<InvestmentType {self.name}>'

class InvestmentTransaction(db.Model):
    __tablename__ = 'investment_transaction'
    id = db.Column(db.Integer, primary_key=True)
    investment_type_id = db.Column(db.Integer, db.ForeignKey('investment_type.id'), nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'buy' veya 'sell'
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __init__(self, investment_type_id, transaction_date, transaction_type, price, quantity, description=None):
        self.investment_type_id = investment_type_id
        self.transaction_date = transaction_date
        self.transaction_type = transaction_type
        self.price = price
        self.quantity = quantity
        self.total_amount = price * quantity
        self.description = description 