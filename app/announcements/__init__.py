from flask import Blueprint

bp = Blueprint("announcements", __name__)

from app.announcements import routes
