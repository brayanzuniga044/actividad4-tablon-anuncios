import os


class Configuracion:
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-desarrollo-cambiar-antes-de-publicar")
    NOMBRE_INSTITUCION = os.environ.get("NOMBRE_INSTITUCION", "Institución Educativa")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///bd_anuncios.sqlite"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
