from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class UserForm(FlaskForm):
    name = StringField("Nombre completo", validators=[DataRequired(), Length(max=100)])
    email = EmailField("Correo electrónico", validators=[DataRequired(), Email(), Length(max=120)])
    username = StringField("Nombre de usuario", validators=[DataRequired(), Length(min=3, max=40)])
    password = PasswordField("Contraseña", validators=[Optional(), Length(min=8, max=128)])
    submit = SubmitField("Guardar usuario")
