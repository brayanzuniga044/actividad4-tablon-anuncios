from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class User(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("nombre", db.String(100), nullable=False)
    email = db.Column("correo", db.String(120), unique=True, nullable=False)
    username = db.Column("nombre_usuario", db.String(40), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        "creado_en",
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    announcements = db.relationship("Announcement", back_populates="author")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Category(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("nombre", db.String(80), unique=True, nullable=False)
    description = db.Column("descripcion", db.String(255), nullable=False, default="")
    announcements = db.relationship("Announcement", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"


class Announcement(db.Model):
    __tablename__ = "anuncios"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column("titulo", db.String(140), nullable=False)
    content = db.Column("contenido", db.Text, nullable=False)
    created_at = db.Column(
        "creado_en",
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    category_id = db.Column(
        "categoria_id",
        db.Integer,
        db.ForeignKey("categorias.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    user_id = db.Column(
        "usuario_id",
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    category = db.relationship("Category", back_populates="announcements")
    author = db.relationship("User", back_populates="announcements")

    def __repr__(self):
        return f"<Announcement {self.title}>"
