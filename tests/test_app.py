import re
import sqlite3

import pytest
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.modelos import Anuncio, Categoria, Usuario


@pytest.fixture()
def app():
    aplicacion = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "clave-pruebas",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "WTF_CSRF_ENABLED": False,
        }
    )
    with aplicacion.app_context():
        db.drop_all()
        db.create_all()
        usuario = Usuario(
            nombre="Ada Lovelace",
            correo="ada@example.com",
            nombre_usuario="ada",
            contrasena_hash=generate_password_hash("password123"),
        )
        categoria = Categoria(nombre="Comunicados", descripcion="Avisos institucionales")
        db.session.add_all([usuario, categoria])
        db.session.commit()
        db.session.add(
            Anuncio(
                titulo="Bienvenida",
                contenido="Inicio del ciclo lectivo.",
                categoria_id=categoria.id,
                usuario_id=usuario.id,
            )
        )
        db.session.commit()
    yield aplicacion
    with aplicacion.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def cliente(app):
    return app.test_client()


def iniciar_sesion(cliente):
    return cliente.post(
        "/ingresar",
        data={"identificador": "ada", "contrasena": "password123"},
        follow_redirects=True,
    )


def test_portada_publica_muestra_y_filtra_anuncios(cliente):
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert "Bienvenida" in respuesta.get_data(as_text=True)
    respuesta = cliente.get("/?q=sin-resultados")
    assert respuesta.status_code == 200
    assert "No hay anuncios para mostrar" in respuesta.get_data(as_text=True)


def test_inicio_sesion_y_proteccion_de_administracion(cliente):
    assert cliente.get("/usuarios/").status_code == 302
    respuesta = cliente.post(
        "/ingresar",
        data={"identificador": "ada", "contrasena": "incorrecta"},
        follow_redirects=True,
    )
    assert "incorrectos" in respuesta.get_data(as_text=True)
    respuesta = iniciar_sesion(cliente)
    assert respuesta.status_code == 200
    assert "Ada Lovelace" in respuesta.get_data(as_text=True)
    assert cliente.get("/usuarios/").status_code == 200


def test_inicio_sesion_rechaza_redirecciones_externas(cliente):
    respuesta = cliente.post(
        "/ingresar?next=//example.com",
        data={"identificador": "ada", "contrasena": "password123"},
    )
    assert respuesta.status_code == 302
    assert respuesta.headers["Location"] == "/"


def test_csrf_en_cierre_de_sesion_y_eliminacion():
    aplicacion = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "clave-pruebas-csrf",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "WTF_CSRF_ENABLED": True,
        }
    )
    with aplicacion.app_context():
        db.create_all()
        usuario = Usuario(
            nombre="Ada Lovelace",
            correo="ada@example.com",
            nombre_usuario="ada",
            contrasena_hash=generate_password_hash("password123"),
        )
        db.session.add_all([usuario, Categoria(nombre="Avisos")])
        db.session.commit()

    cliente = aplicacion.test_client()
    pagina_inicio_sesion = cliente.get("/ingresar").get_data(as_text=True)
    token = re.search(
        r'name="csrf_token" type="hidden" value="([^"]+)"',
        pagina_inicio_sesion,
    ).group(1)
    respuesta = cliente.post(
        "/ingresar",
        data={
            "csrf_token": token,
            "identificador": "ada",
            "contrasena": "password123",
        },
    )
    assert respuesta.status_code == 302

    pagina_categorias = cliente.get("/categorias/").get_data(as_text=True)
    token_eliminar = re.search(
        r'name="csrf_token" value="([^"]+)"', pagina_categorias
    ).group(1)
    respuesta = cliente.post(
        "/categorias/1/eliminar", data={"csrf_token": token_eliminar}
    )
    assert respuesta.status_code == 302
    with aplicacion.app_context():
        assert Categoria.query.count() == 0

    pagina_portada = cliente.get("/").get_data(as_text=True)
    token_salir = re.search(
        r'action="/salir"[^>]*>\s*<input type="hidden" '
        r'name="csrf_token" value="([^"]+)"',
        pagina_portada,
    ).group(1)
    respuesta = cliente.post("/salir", data={"csrf_token": token_salir})
    assert respuesta.status_code == 302
    with aplicacion.app_context():
        db.session.remove()
        db.drop_all()


def test_migra_nombre_de_columna_de_contrasena(tmp_path):
    ruta_bd = tmp_path / "bd_anuncios.sqlite"
    conexion = sqlite3.connect(ruta_bd)
    conexion.execute(
        """
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            correo VARCHAR(120) NOT NULL UNIQUE,
            nombre_usuario VARCHAR(40) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            creado_en DATETIME NOT NULL
        )
        """
    )
    conexion.execute(
        "INSERT INTO usuarios VALUES (1, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
        ("Ada Lovelace", "ada@example.com", "ada", "hash-de-prueba"),
    )
    conexion.commit()
    conexion.close()

    aplicacion = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "clave-migracion",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{ruta_bd.as_posix()}",
        }
    )
    with aplicacion.app_context():
        columnas = {
            columna["name"]
            for columna in db.inspect(db.engine).get_columns("usuarios")
        }
        usuario = db.session.get(Usuario, 1)
        assert "contrasena_hash" in columnas
        assert "password_hash" not in columnas
        assert usuario.contrasena_hash == "hash-de-prueba"
        db.session.remove()
        db.drop_all()


def test_crud_categorias_y_restriccion_de_borrado(app, cliente):
    iniciar_sesion(cliente)
    respuesta = cliente.post(
        "/categorias/nueva",
        data={"nombre": "Actividades", "descripcion": "Agenda"},
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert "Actividades" in respuesta.get_data(as_text=True)

    with app.app_context():
        categoria = Categoria.query.filter_by(nombre="Actividades").one()
        id_categoria = categoria.id
    respuesta = cliente.post(
        f"/categorias/{id_categoria}/editar",
        data={"nombre": "Agenda", "descripcion": "Agenda institucional"},
        follow_redirects=True,
    )
    assert "Agenda" in respuesta.get_data(as_text=True)

    with app.app_context():
        id_categoria = Categoria.query.filter_by(nombre="Comunicados").one().id
    respuesta = cliente.post(
        f"/categorias/{id_categoria}/eliminar", follow_redirects=True
    )
    assert "tiene anuncios asociados" in respuesta.get_data(as_text=True)

    with app.app_context():
        id_categoria = Categoria.query.filter_by(nombre="Agenda").one().id
    respuesta = cliente.post(
        f"/categorias/{id_categoria}/eliminar", follow_redirects=True
    )
    assert "Categoría eliminada" in respuesta.get_data(as_text=True)


def test_crud_usuarios_y_proteccion_de_cuenta_activa(app, cliente):
    iniciar_sesion(cliente)
    respuesta = cliente.post(
        "/usuarios/nuevo",
        data={
            "nombre": "Grace Hopper",
            "correo": "grace@example.com",
            "nombre_usuario": "grace",
            "contrasena": "password456",
        },
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert "Grace Hopper" in respuesta.get_data(as_text=True)

    with app.app_context():
        id_ada = Usuario.query.filter_by(nombre_usuario="ada").one().id
        id_grace = Usuario.query.filter_by(nombre_usuario="grace").one().id
    respuesta = cliente.post(
        f"/usuarios/{id_grace}/editar",
        data={
            "nombre": "Grace Brewster Hopper",
            "correo": "grace@example.com",
            "nombre_usuario": "grace",
            "contrasena": "",
        },
        follow_redirects=True,
    )
    assert "Grace Brewster Hopper" in respuesta.get_data(as_text=True)
    respuesta = cliente.post(
        f"/usuarios/{id_ada}/eliminar", follow_redirects=True
    )
    assert "No puedes eliminar tu propia cuenta" in respuesta.get_data(as_text=True)
    respuesta = cliente.post(
        f"/usuarios/{id_grace}/eliminar", follow_redirects=True
    )
    assert "Usuario eliminado" in respuesta.get_data(as_text=True)


def test_crud_anuncios_y_relaciones_con_portada(app, cliente):
    iniciar_sesion(cliente)
    with app.app_context():
        id_categoria = Categoria.query.filter_by(nombre="Comunicados").one().id
        id_usuario = Usuario.query.filter_by(nombre_usuario="ada").one().id

    respuesta = cliente.post(
        "/anuncios/nuevo",
        data={
            "titulo": "Feria de ciencias",
            "contenido": "Viernes en el auditorio.",
            "categoria_id": id_categoria,
            "usuario_id": id_usuario,
        },
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert "Feria de ciencias" in respuesta.get_data(as_text=True)
    assert "Feria de ciencias" in cliente.get(
        f"/?categoria={id_categoria}"
    ).get_data(as_text=True)

    with app.app_context():
        id_anuncio = Anuncio.query.filter_by(titulo="Feria de ciencias").one().id
    respuesta = cliente.post(
        f"/anuncios/{id_anuncio}/editar",
        data={
            "titulo": "Feria actualizada",
            "contenido": "Nuevo horario.",
            "categoria_id": id_categoria,
            "usuario_id": id_usuario,
        },
        follow_redirects=True,
    )
    assert "Feria actualizada" in respuesta.get_data(as_text=True)
    respuesta = cliente.post(
        f"/anuncios/{id_anuncio}/eliminar", follow_redirects=True
    )
    assert "Anuncio eliminado" in respuesta.get_data(as_text=True)
