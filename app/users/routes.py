from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from app import db
from app.models import Announcement, User
from app.users import bp
from app.users.forms import UserForm


@bp.route("/")
@login_required
def index():
    users = db.session.execute(db.select(User).order_by(User.name)).scalars().all()
    return render_template("users/index.html", users=users)


@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def create():
    form = UserForm()
    if form.validate_on_submit():
        if not form.password.data:
            form.password.errors.append("La contraseña es obligatoria.")
        elif User.query.filter(
            or_(User.username == form.username.data.strip(),
                User.email == form.email.data.strip().lower())
        ).first():
            form.username.errors.append("El usuario o correo ya está registrado.")
        else:
            user = User(
                name=form.name.data.strip(),
                email=form.email.data.strip().lower(),
                username=form.username.data.strip(),
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Usuario registrado correctamente.", "success")
            return redirect(url_for("users.index"))
    return render_template("users/form.html", form=form, page_title="Nuevo usuario")


@bp.route("/<int:user_id>/editar", methods=["GET", "POST"])
@login_required
def edit(user_id):
    user = db.get_or_404(User, user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        duplicate = User.query.filter(
            or_(User.username == form.username.data.strip(),
                User.email == form.email.data.strip().lower()),
            User.id != user.id,
        ).first()
        if duplicate:
            form.username.errors.append("El usuario o correo ya está registrado.")
        else:
            user.name = form.name.data.strip()
            user.email = form.email.data.strip().lower()
            user.username = form.username.data.strip()
            if form.password.data:
                user.set_password(form.password.data)
            db.session.commit()
            flash("Usuario actualizado correctamente.", "success")
            return redirect(url_for("users.index"))
    return render_template("users/form.html", form=form, page_title="Editar usuario")


@bp.route("/<int:user_id>/eliminar", methods=["POST"])
@login_required
def delete(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id:
        flash("No puedes eliminar tu propia cuenta mientras tienes la sesión activa.", "warning")
    elif db.session.execute(
        db.select(Announcement.id).filter_by(user_id=user.id).limit(1)
    ).first():
        flash("No se puede eliminar: el usuario tiene anuncios asociados.", "danger")
    else:
        db.session.delete(user)
        db.session.commit()
        flash("Usuario eliminado.", "success")
    return redirect(url_for("users.index"))
