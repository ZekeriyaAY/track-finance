
from app import db
from app.models import Transaction
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired, ValidationError
import sqlalchemy as sa


class TransactionForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    brand = SelectField('Brand', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')
