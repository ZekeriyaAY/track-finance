from models.__init__ import db
from sqlalchemy import func

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    
    # Relationships
    subcategories = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
    transactions = db.relationship('CashflowTransaction', backref='category', lazy=True)
    
    def get_all_transactions_count(self):
        return self.get_income_count() + self.get_expense_count()

    def get_income_count(self):
        count = len([t for t in self.transactions if t.type == 'income'])
        for subcategory in self.subcategories:
            count += subcategory.get_income_count()
        return count

    def get_expense_count(self):
        count = len([t for t in self.transactions if t.type == 'expense'])
        for subcategory in self.subcategories:
            count += subcategory.get_expense_count()
        return count

    def is_parent(self):
        return self.parent_id is None

    def is_subcategory(self):
        return self.parent_id is not None 