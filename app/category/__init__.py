from flask import Blueprint

bp = Blueprint('category', __name__, template_folder='templates')

from app.category import routes