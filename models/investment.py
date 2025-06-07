from models.__init__ import db
from datetime import datetime

class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('investment_type.id'), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_total_value(self):
        return self.quantity * self.current_price

    def get_profit_loss(self):
        return (self.current_price - self.purchase_price) * self.quantity

    def get_profit_loss_percentage(self):
        if self.purchase_price == 0:
            return 0
        return ((self.current_price - self.purchase_price) / self.purchase_price) * 100 