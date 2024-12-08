from app import db
from app.models import Category
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired
import sqlalchemy as sa


class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_name(self, name):
        category = db.session.scalar(sa.select(Category).where(
            Category.name == name.data))
        if category is not None:
            raise ValidationError('Please use a different category name.')
