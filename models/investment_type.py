from models.__init__ import db
from datetime import datetime

class InvestmentType(db.Model):
    __tablename__ = 'investment_type'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True)  # For internal use (e.g., 'stock', 'crypto')
    icon = db.Column(db.String(50), nullable=False, default='fas fa-chart-pie')  # Font Awesome icon class
    color = db.Column(db.String(7), nullable=False, default='#3B82F6')  # Default blue color
    parent_id = db.Column(db.Integer, db.ForeignKey('investment_type.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = db.relationship('InvestmentType', remote_side=[id], backref='children')
    transactions = db.relationship('InvestmentTransaction', backref='investment_type', lazy=True)

    def __repr__(self):
        return f'<InvestmentType {self.name}>' 