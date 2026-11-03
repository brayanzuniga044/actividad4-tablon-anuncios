from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class FormularioInicioSesion(FlaskForm):
    identificador = StringField("Usuario o correo", validators=[DataRequired(), Length(max=120)])
    contrasena = PasswordField("Contraseña", validators=[DataRequired(), Length(max=128)])
    enviar = SubmitField("Ingresar")
