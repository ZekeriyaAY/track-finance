from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from models.__init__ import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Blueprint'leri import et
from routes.transaction_routes import transaction_bp
from routes.category_routes import category_bp
from routes.tag_routes import tag_bp
from routes.investment_routes import investment_bp
from routes.investment_type_routes import investment_type_bp
from routes.settings_routes import settings_bp

# Blueprint'leri kaydet
app.register_blueprint(transaction_bp)
app.register_blueprint(category_bp)
app.register_blueprint(tag_bp)
app.register_blueprint(investment_bp)
app.register_blueprint(investment_type_bp)
app.register_blueprint(settings_bp)

@app.route('/')
def index():
    return redirect(url_for('transaction.index'))

if __name__ == '__main__':
    app.run(debug=True) 