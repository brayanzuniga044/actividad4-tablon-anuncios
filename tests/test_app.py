import re

import pytest
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import Announcement, Category, User


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-key",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "WTF_CSRF_ENABLED": False,
        }
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = User(
            name="Ada Lovelace",
            email="ada@example.com",
            username="ada",
            password_hash=generate_password_hash("password123"),
        )
        category = Category(name="Comunicados", description="Avisos institucionales")
        db.session.add_all([user, category])
        db.session.commit()
        db.session.add(
            Announcement(
                title="Bienvenida",
                content="Inicio del ciclo lectivo.",
                category_id=category.id,
                user_id=user.id,
            )
        )
        db.session.commit()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client):
    return client.post(
        "/ingresar",
        data={"identity": "ada", "password": "password123"},
        follow_redirects=True,
    )


def test_public_home_shows_announcements_and_filters(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Bienvenida" in response.get_data(as_text=True)
    assert client.get("/?q=sin-resultados").status_code == 200
    assert "No hay anuncios para mostrar" in client.get(
        "/?q=sin-resultados"
    ).get_data(as_text=True)


def test_login_and_protected_user_management(client):
    assert client.get("/usuarios/").status_code == 302
    rejected = client.post(
        "/ingresar",
        data={"identity": "ada", "password": "incorrecta"},
        follow_redirects=True,
    )
    assert "incorrectos" in rejected.get_data(as_text=True)
    response = login(client)
    assert response.status_code == 200
    assert "Ada Lovelace" in response.get_data(as_text=True)
    assert client.get("/usuarios/").status_code == 200


def test_login_rejects_external_next_url(client):
    response = client.post(
        "/ingresar?next=//example.com",
        data={"identity": "ada", "password": "password123"},
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_csrf_protected_logout_and_delete_forms():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "csrf-test-key",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "WTF_CSRF_ENABLED": True,
        }
    )
    with app.app_context():
        db.create_all()
        user = User(
            name="Ada Lovelace",
            email="ada@example.com",
            username="ada",
            password_hash=generate_password_hash("password123"),
        )
        db.session.add_all([user, Category(name="Avisos")])
        db.session.commit()

    client = app.test_client()
    login_page = client.get("/ingresar").get_data(as_text=True)
    token = re.search(
        r'name="csrf_token" type="hidden" value="([^"]+)"', login_page
    ).group(1)
    response = client.post(
        "/ingresar",
        data={"csrf_token": token, "identity": "ada", "password": "password123"},
    )
    assert response.status_code == 302

    categories_page = client.get("/categorias/").get_data(as_text=True)
    delete_token = re.search(
        r'name="csrf_token" value="([^"]+)"', categories_page
    ).group(1)
    response = client.post("/categorias/1/eliminar", data={"csrf_token": delete_token})
    assert response.status_code == 302
    with app.app_context():
        assert Category.query.count() == 0

    home_page = client.get("/").get_data(as_text=True)
    logout_token = re.search(
        r'action="/salir"[^>]*>\s*<input type="hidden" name="csrf_token" value="([^"]+)"',
        home_page,
    ).group(1)
    response = client.post("/salir", data={"csrf_token": logout_token})
    assert response.status_code == 302
    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_category_crud_and_restrict_delete_when_in_use(app, client):
    login(client)
    response = client.post(
        "/categorias/nueva",
        data={"name": "Actividades", "description": "Agenda"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Actividades" in response.get_data(as_text=True)

    with app.app_context():
        category = Category.query.filter_by(name="Actividades").one()
        category_id = category.id
    response = client.post(
        f"/categorias/{category_id}/editar",
        data={"name": "Agenda", "description": "Agenda institucional"},
        follow_redirects=True,
    )
    assert "Agenda" in response.get_data(as_text=True)

    with app.app_context():
        category = Category.query.filter_by(name="Comunicados").one()
        category_id = category.id
    response = client.post(
        f"/categorias/{category_id}/eliminar", follow_redirects=True
    )
    assert "tiene anuncios asociados" in response.get_data(as_text=True)

    with app.app_context():
        category = Category.query.filter_by(name="Agenda").one()
        category_id = category.id
    response = client.post(
        f"/categorias/{category_id}/eliminar", follow_redirects=True
    )
    assert "Categoría eliminada" in response.get_data(as_text=True)


def test_user_crud_and_prevent_self_deletion(app, client):
    login(client)
    response = client.post(
        "/usuarios/nuevo",
        data={
            "name": "Grace Hopper",
            "email": "grace@example.com",
            "username": "grace",
            "password": "password456",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Grace Hopper" in response.get_data(as_text=True)

    with app.app_context():
        ada_id = User.query.filter_by(username="ada").one().id
        grace_id = User.query.filter_by(username="grace").one().id
    response = client.post(
        f"/usuarios/{grace_id}/editar",
        data={
            "name": "Grace Brewster Hopper",
            "email": "grace@example.com",
            "username": "grace",
            "password": "",
        },
        follow_redirects=True,
    )
    assert "Grace Brewster Hopper" in response.get_data(as_text=True)
    response = client.post(f"/usuarios/{ada_id}/eliminar", follow_redirects=True)
    assert "No puedes eliminar tu propia cuenta" in response.get_data(as_text=True)
    response = client.post(f"/usuarios/{grace_id}/eliminar", follow_redirects=True)
    assert "Usuario eliminado" in response.get_data(as_text=True)


def test_announcement_crud_associations_and_home_filter(app, client):
    login(client)
    with app.app_context():
        category_id = Category.query.filter_by(name="Comunicados").one().id
        user_id = User.query.filter_by(username="ada").one().id

    response = client.post(
        "/anuncios/nuevo",
        data={
            "title": "Feria de ciencias",
            "content": "Viernes en el auditorio.",
            "category_id": category_id,
            "user_id": user_id,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Feria de ciencias" in response.get_data(as_text=True)
    assert "Feria de ciencias" in client.get(
        f"/?categoria={category_id}"
    ).get_data(as_text=True)

    with app.app_context():
        announcement_id = Announcement.query.filter_by(
            title="Feria de ciencias"
        ).one().id
    response = client.post(
        f"/anuncios/{announcement_id}/editar",
        data={
            "title": "Feria actualizada",
            "content": "Nuevo horario.",
            "category_id": category_id,
            "user_id": user_id,
        },
        follow_redirects=True,
    )
    assert "Feria actualizada" in response.get_data(as_text=True)
    response = client.post(
        f"/anuncios/{announcement_id}/eliminar", follow_redirects=True
    )
    assert "Anuncio eliminado" in response.get_data(as_text=True)
