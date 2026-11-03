from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class AnnouncementForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired(), Length(max=140)])
    content = TextAreaField("Contenido", validators=[DataRequired(), Length(max=10000)])
    category_id = SelectField("Categoría", coerce=int, validators=[DataRequired()])
    user_id = SelectField("Publicado por", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Guardar anuncio")
