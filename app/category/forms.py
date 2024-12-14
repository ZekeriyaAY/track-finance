from app import db
from app.models import Category
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired
import sqlalchemy as sa


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    type = SelectField('Type', choices=[('Expense', 'Expense'), ('Income', 'Income')],
                       validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_name(self, name):
        category = db.session.scalar(sa.select(Category).where(
            Category.name == name.data, Category.type == self.type.data, Category.user_id == current_user.id))
        if category is not None:
            raise ValidationError('Please use a different category name.')
