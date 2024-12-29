from app import db
from app.models import Transaction
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired, ValidationError
import sqlalchemy as sa


class TransactionForm(FlaskForm):
    name = StringField('Transaction Name', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    brand_id = SelectField('Brand', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')
