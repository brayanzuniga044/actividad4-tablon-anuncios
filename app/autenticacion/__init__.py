from flask import Blueprint

bp = Blueprint("autenticacion", __name__)

from app.autenticacion import rutas
