import os

import click
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicia sesión para continuar."
    login_manager.login_message_category = "warning"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    from app.announcements import bp as announcements_bp
    from app.auth import bp as auth_bp
    from app.categories import bp as categories_bp
    from app.main import bp as main_bp
    from app.users import bp as users_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp, url_prefix="/usuarios")
    app.register_blueprint(categories_bp, url_prefix="/categorias")
    app.register_blueprint(announcements_bp, url_prefix="/anuncios")

    @app.cli.command("init-db")
    def init_db():
        """Create the database tables."""
        db.create_all()
        click.echo("Base de datos inicializada.")

    @app.cli.command("create-admin")
    @click.option("--nombre", prompt="Nombre completo")
    @click.option("--correo", prompt="Correo electrónico")
    @click.option("--usuario", prompt="Nombre de usuario")
    @click.password_option("--password", confirmation_prompt=True)
    def create_admin(nombre, correo, usuario, password):
        """Create an initial account for the notice board."""
        if User.query.filter(
            (User.username == usuario) | (User.email == correo)
        ).first():
            raise click.ClickException("Ya existe ese usuario o correo.")
        db.session.add(
            User(
                name=nombre.strip(),
                email=correo.strip().lower(),
                username=usuario.strip(),
                password_hash=generate_password_hash(password),
            )
        )
        db.session.commit()
        click.echo("Cuenta creada. Ya puedes iniciar sesión.")

    with app.app_context():
        db.create_all()

    return app
