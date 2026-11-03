from flask import flash, redirect, render_template, url_for
from flask_login import login_required

from app import db
from app.categorias import bp
from app.categorias.formularios import FormularioCategoria
from app.modelos import Anuncio, Categoria


@bp.route("/")
@login_required
def lista():
    categorias = db.session.execute(
        db.select(Categoria).order_by(Categoria.nombre)
    ).scalars().all()
    return render_template("categorias/lista.html", categorias=categorias)


@bp.route("/nueva", methods=["GET", "POST"])
@login_required
def crear():
    formulario = FormularioCategoria()
    if formulario.validate_on_submit():
        nombre = formulario.nombre.data.strip()
        if Categoria.query.filter_by(nombre=nombre).first():
            formulario.nombre.errors.append("Ya existe una categoría con ese nombre.")
        else:
            db.session.add(
                Categoria(
                    nombre=nombre,
                    descripcion=(formulario.descripcion.data or "").strip(),
                )
            )
            db.session.commit()
            flash("Categoría registrada correctamente.", "success")
            return redirect(url_for("categorias.lista"))
    return render_template(
        "categorias/formulario.html",
        formulario=formulario,
        titulo_pagina="Nueva categoría",
    )


@bp.route("/<int:id_categoria>/editar", methods=["GET", "POST"])
@login_required
def editar(id_categoria):
    categoria = db.get_or_404(Categoria, id_categoria)
    formulario = FormularioCategoria(obj=categoria)
    if formulario.validate_on_submit():
        nombre = formulario.nombre.data.strip()
        duplicada = Categoria.query.filter(
            Categoria.nombre == nombre, Categoria.id != categoria.id
        ).first()
        if duplicada:
            formulario.nombre.errors.append("Ya existe una categoría con ese nombre.")
        else:
            categoria.nombre = nombre
            categoria.descripcion = (formulario.descripcion.data or "").strip()
            db.session.commit()
            flash("Categoría actualizada correctamente.", "success")
            return redirect(url_for("categorias.lista"))
    return render_template(
        "categorias/formulario.html",
        formulario=formulario,
        titulo_pagina="Editar categoría",
    )


@bp.route("/<int:id_categoria>/eliminar", methods=["POST"])
@login_required
def eliminar(id_categoria):
    categoria = db.get_or_404(Categoria, id_categoria)
    if db.session.execute(
        db.select(Anuncio.id).filter_by(categoria_id=categoria.id).limit(1)
    ).first():
        flash("No se puede eliminar: la categoría tiene anuncios asociados.", "danger")
    else:
        db.session.delete(categoria)
        db.session.commit()
        flash("Categoría eliminada.", "success")
    return redirect(url_for("categorias.lista"))
