from urllib.parse import urlsplit

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import or_

from app.autenticacion import bp
from app.autenticacion.formularios import FormularioInicioSesion
from app.modelos import Usuario


@bp.route("/ingresar", methods=["GET", "POST"])
def iniciar_sesion():
    if current_user.is_authenticated:
        return redirect(url_for("inicio.portada"))
    formulario = FormularioInicioSesion()
    if formulario.validate_on_submit():
        usuario = Usuario.query.filter(
            or_(
                Usuario.nombre_usuario == formulario.identificador.data.strip(),
                Usuario.correo == formulario.identificador.data.strip().lower(),
            )
        ).first()
        if usuario and usuario.verificar_contrasena(formulario.contrasena.data):
            login_user(usuario)
            pagina_siguiente = request.args.get("next")
            if pagina_siguiente:
                destino = urlsplit(pagina_siguiente)
                if (
                    destino.scheme
                    or destino.netloc
                    or not destino.path.startswith("/")
                    or destino.path.startswith("//")
                    or "\\" in pagina_siguiente
                ):
                    pagina_siguiente = None
            return redirect(pagina_siguiente or url_for("inicio.portada"))
        flash("Usuario, correo o contraseña incorrectos.", "danger")
    return render_template(
        "autenticacion/iniciar_sesion.html", formulario=formulario
    )


@bp.route("/salir", methods=["POST"])
def cerrar_sesion():
    if current_user.is_authenticated:
        logout_user()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("autenticacion.iniciar_sesion"))
