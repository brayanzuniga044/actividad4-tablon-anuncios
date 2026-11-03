from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class FormularioCategoria(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=80)])
    descripcion = TextAreaField("Descripción", validators=[Optional(), Length(max=255)])
    enviar = SubmitField("Guardar categoría")
