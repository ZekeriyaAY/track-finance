from models import db
from datetime import datetime, date

# CashflowTransaction-Tag relationship table
cashflow_transaction_tags = db.Table('cashflow_transaction_tags',
    db.Column('cashflow_transaction_id', db.Integer, db.ForeignKey('cashflow_transaction.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class CashflowTransaction(db.Model):
    __tablename__ = 'cashflow_transaction'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    source = db.Column(db.String(20), default='manual')  # 'manual' / 'excel_import'
    tags = db.relationship('Tag', secondary='cashflow_transaction_tags', back_populates='transactions')