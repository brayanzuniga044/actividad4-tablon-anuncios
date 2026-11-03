from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from app import db
from app.modelos import Anuncio, Usuario
from app.usuarios import bp
from app.usuarios.formularios import FormularioUsuario


@bp.route("/")
@login_required
def lista():
    usuarios = db.session.execute(
        db.select(Usuario).order_by(Usuario.nombre)
    ).scalars().all()
    return render_template("usuarios/lista.html", usuarios=usuarios)


@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def crear():
    formulario = FormularioUsuario()
    if formulario.validate_on_submit():
        if not formulario.contrasena.data:
            formulario.contrasena.errors.append("La contraseña es obligatoria.")
        elif Usuario.query.filter(
            or_(Usuario.nombre_usuario == formulario.nombre_usuario.data.strip(),
                Usuario.correo == formulario.correo.data.strip().lower())
        ).first():
            formulario.nombre_usuario.errors.append("El usuario o correo ya está registrado.")
        else:
            usuario = Usuario(
                nombre=formulario.nombre.data.strip(),
                correo=formulario.correo.data.strip().lower(),
                nombre_usuario=formulario.nombre_usuario.data.strip(),
            )
            usuario.establecer_contrasena(formulario.contrasena.data)
            db.session.add(usuario)
            db.session.commit()
            flash("Usuario registrado correctamente.", "success")
            return redirect(url_for("usuarios.lista"))
    return render_template(
        "usuarios/formulario.html",
        formulario=formulario,
        titulo_pagina="Nuevo usuario",
    )


@bp.route("/<int:id_usuario>/editar", methods=["GET", "POST"])
@login_required
def editar(id_usuario):
    usuario = db.get_or_404(Usuario, id_usuario)
    formulario = FormularioUsuario(obj=usuario)
    if formulario.validate_on_submit():
        duplicado = Usuario.query.filter(
            or_(Usuario.nombre_usuario == formulario.nombre_usuario.data.strip(),
                Usuario.correo == formulario.correo.data.strip().lower()),
            Usuario.id != usuario.id,
        ).first()
        if duplicado:
            formulario.nombre_usuario.errors.append("El usuario o correo ya está registrado.")
        else:
            usuario.nombre = formulario.nombre.data.strip()
            usuario.correo = formulario.correo.data.strip().lower()
            usuario.nombre_usuario = formulario.nombre_usuario.data.strip()
            if formulario.contrasena.data:
                usuario.establecer_contrasena(formulario.contrasena.data)
            db.session.commit()
            flash("Usuario actualizado correctamente.", "success")
            return redirect(url_for("usuarios.lista"))
    return render_template(
        "usuarios/formulario.html",
        formulario=formulario,
        titulo_pagina="Editar usuario",
    )


@bp.route("/<int:id_usuario>/eliminar", methods=["POST"])
@login_required
def eliminar(id_usuario):
    usuario = db.get_or_404(Usuario, id_usuario)
    if usuario.id == current_user.id:
        flash("No puedes eliminar tu propia cuenta mientras tienes la sesión activa.", "warning")
    elif db.session.execute(
        db.select(Anuncio.id).filter_by(usuario_id=usuario.id).limit(1)
    ).first():
        flash("No se puede eliminar: el usuario tiene anuncios asociados.", "danger")
    else:
        db.session.delete(usuario)
        db.session.commit()
        flash("Usuario eliminado.", "success")
    return redirect(url_for("usuarios.lista"))
