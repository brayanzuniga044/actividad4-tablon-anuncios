import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-before-deployment")
    INSTITUTION_NAME = os.environ.get("INSTITUTION_NAME", "Institución Educativa")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///bd_anuncios.sqlite"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
