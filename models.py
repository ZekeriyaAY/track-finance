class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    history = db.relationship('InvestmentHistory', backref='investment', lazy=True, cascade='all, delete-orphan')
    
    def get_total_value(self):
        return self.current_price * self.quantity
    
    def get_purchase_value(self):
        return self.purchase_price * self.quantity
    
    def get_profit_loss(self):
        return self.get_total_value() - self.get_purchase_value()
    
    def get_profit_loss_percentage(self):
        if self.get_purchase_value() == 0:
            return 0
        return (self.get_profit_loss() / self.get_purchase_value()) * 100 