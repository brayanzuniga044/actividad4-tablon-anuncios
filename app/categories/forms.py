from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class CategoryForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(max=80)])
    description = TextAreaField("Descripción", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Guardar categoría")
