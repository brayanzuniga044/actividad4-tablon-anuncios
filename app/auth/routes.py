from urllib.parse import urlsplit

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import or_

from app.auth import bp
from app.auth.forms import LoginForm
from app.models import User


@bp.route("/ingresar", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        account = User.query.filter(
            or_(
                User.username == form.identity.data.strip(),
                User.email == form.identity.data.strip().lower(),
            )
        ).first()
        if account and account.check_password(form.password.data):
            login_user(account)
            next_page = request.args.get("next")
            if next_page:
                target = urlsplit(next_page)
                if (
                    target.scheme
                    or target.netloc
                    or not target.path.startswith("/")
                    or target.path.startswith("//")
                    or "\\" in next_page
                ):
                    next_page = None
            return redirect(next_page or url_for("main.index"))
        flash("Usuario, correo o contraseña incorrectos.", "danger")
    return render_template("auth/login.html", form=form)


@bp.route("/salir", methods=["POST"])
def logout():
    if current_user.is_authenticated:
        logout_user()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("auth.login"))
