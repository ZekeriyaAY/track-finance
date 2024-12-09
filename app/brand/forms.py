from app import db
from app.models import Brand
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired
import sqlalchemy as sa


class BrandForm(FlaskForm):
    name = StringField('Brand Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_name(self, name):
        brand = db.session.scalar(sa.select(Brand).where(
            Brand.name == name.data))
        if brand is not None:
            raise ValidationError('Please use a different brand name.')
