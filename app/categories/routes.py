from flask import flash, redirect, render_template, url_for
from flask_login import login_required

from app import db
from app.categories import bp
from app.categories.forms import CategoryForm
from app.models import Announcement, Category


@bp.route("/")
@login_required
def index():
    categories = db.session.execute(
        db.select(Category).order_by(Category.name)
    ).scalars().all()
    return render_template("categories/index.html", categories=categories)


@bp.route("/nueva", methods=["GET", "POST"])
@login_required
def create():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        if Category.query.filter_by(name=name).first():
            form.name.errors.append("Ya existe una categoría con ese nombre.")
        else:
            db.session.add(Category(name=name, description=(form.description.data or "").strip()))
            db.session.commit()
            flash("Categoría registrada correctamente.", "success")
            return redirect(url_for("categories.index"))
    return render_template("categories/form.html", form=form, page_title="Nueva categoría")


@bp.route("/<int:category_id>/editar", methods=["GET", "POST"])
@login_required
def edit(category_id):
    category = db.get_or_404(Category, category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        name = form.name.data.strip()
        duplicate = Category.query.filter(
            Category.name == name, Category.id != category.id
        ).first()
        if duplicate:
            form.name.errors.append("Ya existe una categoría con ese nombre.")
        else:
            category.name = name
            category.description = (form.description.data or "").strip()
            db.session.commit()
            flash("Categoría actualizada correctamente.", "success")
            return redirect(url_for("categories.index"))
    return render_template("categories/form.html", form=form, page_title="Editar categoría")


@bp.route("/<int:category_id>/eliminar", methods=["POST"])
@login_required
def delete(category_id):
    category = db.get_or_404(Category, category_id)
    if db.session.execute(
        db.select(Announcement.id).filter_by(category_id=category.id).limit(1)
    ).first():
        flash("No se puede eliminar: la categoría tiene anuncios asociados.", "danger")
    else:
        db.session.delete(category)
        db.session.commit()
        flash("Categoría eliminada.", "success")
    return redirect(url_for("categories.index"))
