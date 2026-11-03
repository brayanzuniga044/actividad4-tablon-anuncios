import os

import click
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash

from configuracion import Configuracion

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Configuracion)
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "autenticacion.iniciar_sesion"
    login_manager.login_message = "Inicia sesión para continuar."
    login_manager.login_message_category = "warning"

    from app.modelos import Usuario

    @login_manager.user_loader
    def cargar_usuario(id_usuario):
        try:
            return db.session.get(Usuario, int(id_usuario))
        except (TypeError, ValueError):
            return None

    from app.anuncios import bp as anuncios_bp
    from app.autenticacion import bp as autenticacion_bp
    from app.categorias import bp as categorias_bp
    from app.inicio import bp as inicio_bp
    from app.usuarios import bp as usuarios_bp

    app.register_blueprint(inicio_bp)
    app.register_blueprint(autenticacion_bp)
    app.register_blueprint(usuarios_bp, url_prefix="/usuarios")
    app.register_blueprint(categorias_bp, url_prefix="/categorias")
    app.register_blueprint(anuncios_bp, url_prefix="/anuncios")

    with app.app_context():
        inspector = inspect(db.engine)
        if inspector.has_table("usuarios"):
            columnas = {columna["name"] for columna in inspector.get_columns("usuarios")}
            if "password_hash" in columnas and "contrasena_hash" not in columnas:
                if db.engine.dialect.name == "sqlite":
                    sql_migracion = (
                        "ALTER TABLE usuarios RENAME COLUMN "
                        "password_hash TO contrasena_hash"
                    )
                elif db.engine.dialect.name == "mysql":
                    sql_migracion = (
                        "ALTER TABLE usuarios CHANGE password_hash "
                        "contrasena_hash VARCHAR(255) NOT NULL"
                    )
                else:
                    raise RuntimeError(
                        "No se puede migrar password_hash en este motor de base de datos."
                    )
                db.session.execute(text(sql_migracion))
                db.session.commit()

    @app.cli.command("inicializar-bd")
    def inicializar_bd():
        """Crea las tablas de la base de datos."""
        db.create_all()
        click.echo("Base de datos inicializada.")

    @app.cli.command("crear-administrador")
    @click.option("--nombre", prompt="Nombre completo")
    @click.option("--correo", prompt="Correo electrónico")
    @click.option("--nombre-usuario", prompt="Nombre de usuario")
    @click.password_option("--contrasena", confirmation_prompt=True)
    def crear_administrador(nombre, correo, nombre_usuario, contrasena):
        """Crea la cuenta inicial para el tablón de anuncios."""
        if Usuario.query.filter(
            (Usuario.nombre_usuario == nombre_usuario)
            | (Usuario.correo == correo)
        ).first():
            raise click.ClickException("Ya existe ese usuario o correo.")
        db.session.add(
            Usuario(
                nombre=nombre.strip(),
                correo=correo.strip().lower(),
                nombre_usuario=nombre_usuario.strip(),
                contrasena_hash=generate_password_hash(contrasena),
            )
        )
        db.session.commit()
        click.echo("Cuenta creada. Ya puedes iniciar sesión.")

    with app.app_context():
        db.create_all()

    return app
