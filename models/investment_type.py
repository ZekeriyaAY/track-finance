from models.__init__ import db
from datetime import datetime

class InvestmentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True)  # For internal use (e.g., 'stock', 'crypto')
    parent_id = db.Column(db.Integer, db.ForeignKey('investment_type.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = db.relationship('InvestmentType', remote_side=[id], backref='children')
    investments = db.relationship('Investment', backref='investment_type', lazy=True)

    def __repr__(self):
        return f'<InvestmentType {self.name}>' 