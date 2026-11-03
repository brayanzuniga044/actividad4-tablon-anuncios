from flask import Blueprint

bp = Blueprint("anuncios", __name__)

from app.anuncios import rutas
