from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class FormularioUsuario(FlaskForm):
    nombre = StringField("Nombre completo", validators=[DataRequired(), Length(max=100)])
    correo = EmailField("Correo electrónico", validators=[DataRequired(), Email(), Length(max=120)])
    nombre_usuario = StringField("Nombre de usuario", validators=[DataRequired(), Length(min=3, max=40)])
    contrasena = PasswordField("Contraseña", validators=[Optional(), Length(min=8, max=128)])
    enviar = SubmitField("Guardar usuario")
