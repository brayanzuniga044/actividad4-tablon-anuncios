from flask import render_template, request
from sqlalchemy import or_

from app import db
from app.inicio import bp
from app.modelos import Anuncio, Categoria


@bp.route("/")
def portada():
    consulta = Anuncio.query
    busqueda = request.args.get("q", "").strip()
    id_categoria = request.args.get("categoria", type=int)
    if busqueda:
        consulta = consulta.filter(
            or_(
                Anuncio.titulo.ilike(f"%{busqueda}%"),
                Anuncio.contenido.ilike(f"%{busqueda}%"),
            )
        )
    if id_categoria:
        consulta = consulta.filter(Anuncio.categoria_id == id_categoria)
    anuncios = consulta.order_by(Anuncio.creado_en.desc()).all()
    categorias = db.session.execute(
        db.select(Categoria).order_by(Categoria.nombre)
    ).scalars().all()
    return render_template(
        "inicio/portada.html",
        anuncios=anuncios,
        categorias=categorias,
        busqueda=busqueda,
        categoria_seleccionada=id_categoria,
    )
