from flask import flash, redirect, render_template, url_for
from flask_login import login_required

from app import db
from app.announcements import bp
from app.announcements.forms import AnnouncementForm
from app.models import Announcement, Category, User


def populate_choices(form):
    form.category_id.choices = [
        (category.id, category.name)
        for category in db.session.execute(
            db.select(Category).order_by(Category.name)
        ).scalars()
    ]
    form.user_id.choices = [
        (user.id, f"{user.name} (@{user.username})")
        for user in db.session.execute(db.select(User).order_by(User.name)).scalars()
    ]


@bp.route("/")
@login_required
def index():
    announcements = db.session.execute(
        db.select(Announcement).order_by(Announcement.created_at.desc())
    ).scalars().all()
    return render_template("announcements/index.html", announcements=announcements)


@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def create():
    form = AnnouncementForm()
    populate_choices(form)
    if form.validate_on_submit():
        announcement = Announcement(
            title=form.title.data.strip(),
            content=form.content.data.strip(),
            category_id=form.category_id.data,
            user_id=form.user_id.data,
        )
        db.session.add(announcement)
        db.session.commit()
        flash("Anuncio publicado correctamente.", "success")
        return redirect(url_for("announcements.index"))
    return render_template(
        "announcements/form.html", form=form, page_title="Nuevo anuncio"
    )


@bp.route("/<int:announcement_id>/editar", methods=["GET", "POST"])
@login_required
def edit(announcement_id):
    announcement = db.get_or_404(Announcement, announcement_id)
    form = AnnouncementForm(obj=announcement)
    populate_choices(form)
    if form.validate_on_submit():
        announcement.title = form.title.data.strip()
        announcement.content = form.content.data.strip()
        announcement.category_id = form.category_id.data
        announcement.user_id = form.user_id.data
        db.session.commit()
        flash("Anuncio actualizado correctamente.", "success")
        return redirect(url_for("announcements.index"))
    return render_template(
        "announcements/form.html", form=form, page_title="Editar anuncio"
    )


@bp.route("/<int:announcement_id>/eliminar", methods=["POST"])
@login_required
def delete(announcement_id):
    announcement = db.get_or_404(Announcement, announcement_id)
    db.session.delete(announcement)
    db.session.commit()
    flash("Anuncio eliminado.", "success")
    return redirect(url_for("announcements.index"))
