from flask import flash, redirect, render_template, url_for
from flask_login import login_required

from app import db
from app.anuncios import bp
from app.anuncios.formularios import FormularioAnuncio
from app.modelos import Anuncio, Categoria, Usuario


def cargar_opciones(formulario):
    formulario.categoria_id.choices = [
        (categoria.id, categoria.nombre)
        for categoria in db.session.execute(
            db.select(Categoria).order_by(Categoria.nombre)
        ).scalars()
    ]
    formulario.usuario_id.choices = [
        (usuario.id, f"{usuario.nombre} (@{usuario.nombre_usuario})")
        for usuario in db.session.execute(
            db.select(Usuario).order_by(Usuario.nombre)
        ).scalars()
    ]


@bp.route("/")
@login_required
def lista():
    anuncios = db.session.execute(
        db.select(Anuncio).order_by(Anuncio.creado_en.desc())
    ).scalars().all()
    return render_template("anuncios/lista.html", anuncios=anuncios)


@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def crear():
    formulario = FormularioAnuncio()
    cargar_opciones(formulario)
    if formulario.validate_on_submit():
        anuncio = Anuncio(
            titulo=formulario.titulo.data.strip(),
            contenido=formulario.contenido.data.strip(),
            categoria_id=formulario.categoria_id.data,
            usuario_id=formulario.usuario_id.data,
        )
        db.session.add(anuncio)
        db.session.commit()
        flash("Anuncio publicado correctamente.", "success")
        return redirect(url_for("anuncios.lista"))
    return render_template(
        "anuncios/formulario.html",
        formulario=formulario,
        titulo_pagina="Nuevo anuncio",
    )


@bp.route("/<int:id_anuncio>/editar", methods=["GET", "POST"])
@login_required
def editar(id_anuncio):
    anuncio = db.get_or_404(Anuncio, id_anuncio)
    formulario = FormularioAnuncio(obj=anuncio)
    cargar_opciones(formulario)
    if formulario.validate_on_submit():
        anuncio.titulo = formulario.titulo.data.strip()
        anuncio.contenido = formulario.contenido.data.strip()
        anuncio.categoria_id = formulario.categoria_id.data
        anuncio.usuario_id = formulario.usuario_id.data
        db.session.commit()
        flash("Anuncio actualizado correctamente.", "success")
        return redirect(url_for("anuncios.lista"))
    return render_template(
        "anuncios/formulario.html",
        formulario=formulario,
        titulo_pagina="Editar anuncio",
    )


@bp.route("/<int:id_anuncio>/eliminar", methods=["POST"])
@login_required
def eliminar(id_anuncio):
    anuncio = db.get_or_404(Anuncio, id_anuncio)
    db.session.delete(anuncio)
    db.session.commit()
    flash("Anuncio eliminado.", "success")
    return redirect(url_for("anuncios.lista"))
