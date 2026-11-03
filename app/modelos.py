from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    nombre_usuario = db.Column(db.String(40), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(255), nullable=False)
    creado_en = db.Column(
        "creado_en",
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    anuncios = db.relationship("Anuncio", back_populates="autor")

    def establecer_contrasena(self, contrasena):
        self.contrasena_hash = generate_password_hash(contrasena)

    def verificar_contrasena(self, contrasena):
        return check_password_hash(self.contrasena_hash, contrasena)

    def __repr__(self):
        return f"<Usuario {self.nombre_usuario}>"


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    descripcion = db.Column(db.String(255), nullable=False, default="")
    anuncios = db.relationship("Anuncio", back_populates="categoria")

    def __repr__(self):
        return f"<Categoria {self.nombre}>"


class Anuncio(db.Model):
    __tablename__ = "anuncios"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(140), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    creado_en = db.Column(
        "creado_en",
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    categoria_id = db.Column(
        db.Integer,
        db.ForeignKey("categorias.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    categoria = db.relationship("Categoria", back_populates="anuncios")
    autor = db.relationship("Usuario", back_populates="anuncios")

    def __repr__(self):
        return f"<Anuncio {self.titulo}>"
