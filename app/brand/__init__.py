from flask import Blueprint

bp = Blueprint('brand', __name__, template_folder='templates')

from app.brand import routes