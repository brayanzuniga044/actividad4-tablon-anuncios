from flask import Blueprint

bp = Blueprint("inicio", __name__)

from app.inicio import rutas
