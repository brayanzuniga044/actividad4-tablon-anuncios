from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class FormularioAnuncio(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired(), Length(max=140)])
    contenido = TextAreaField("Contenido", validators=[DataRequired(), Length(max=10000)])
    categoria_id = SelectField("Categoría", coerce=int, validators=[DataRequired()])
    usuario_id = SelectField("Publicado por", coerce=int, validators=[DataRequired()])
    enviar = SubmitField("Guardar anuncio")
