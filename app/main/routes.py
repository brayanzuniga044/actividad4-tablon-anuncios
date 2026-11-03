from flask import render_template, request
from sqlalchemy import or_

from app import db
from app.main import bp
from app.models import Announcement, Category


@bp.route("/")
def index():
    query = Announcement.query
    search = request.args.get("q", "").strip()
    category_id = request.args.get("categoria", type=int)
    if search:
        query = query.filter(
            or_(
                Announcement.title.ilike(f"%{search}%"),
                Announcement.content.ilike(f"%{search}%"),
            )
        )
    if category_id:
        query = query.filter(Announcement.category_id == category_id)
    announcements = query.order_by(Announcement.created_at.desc()).all()
    categories = db.session.execute(
        db.select(Category).order_by(Category.name)
    ).scalars().all()
    return render_template(
        "main/index.html",
        announcements=announcements,
        categories=categories,
        search=search,
        selected_category=category_id,
    )
