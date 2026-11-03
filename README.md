# Actividad N.º 4 — Tablón de anuncios con Flask

Aplicación web modular para publicar y administrar anuncios institucionales. Usa Flask, SQLAlchemy, Flask-Login, formularios protegidos contra CSRF y Bootstrap 5.

## Funcionalidades

- Portada pública con búsqueda y filtro por categoría.
- Inicio de sesión por nombre de usuario o correo; las contraseñas se guardan mediante hash.
- Administración autenticada: altas, consultas, modificaciones y bajas de usuarios, categorías y anuncios.
- Cada anuncio se relaciona con la categoría y el usuario que lo publica.
- No se permite eliminar usuarios o categorías con anuncios relacionados ni la cuenta que tiene la sesión activa.
- Interfaz adaptable con cabecera, menú y pie comunes.
- Patrón Application Factory mediante `create_app()` y rutas organizadas en Blueprints.
- SQLite listo para usar y conexión configurable con MySQL/MariaDB de XAMPP.

## Requisitos

- Python 3.10 o posterior.
- Para MySQL, tener el servicio de MySQL/MariaDB iniciado, por ejemplo, desde XAMPP.

## Instalación y ejecución

En PowerShell, desde la carpeta del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
flask --app iniciar.py inicializar-bd
flask --app iniciar.py crear-administrador
flask --app iniciar.py run
```

Abre <http://127.0.0.1:5000/>. El comando `crear-administrador` solicita nombre, correo, nombre de usuario y contraseña; el proyecto no contiene una cuenta predeterminada.

## Conexión con MySQL/MariaDB de XAMPP

1. Inicia MySQL desde XAMPP.
2. En phpMyAdmin importa [`schema.sql`](./schema.sql), que crea la base `bd_anuncios` y sus tablas.
3. En PowerShell configura la conexión y el nombre de la institución:

```powershell
$env:DATABASE_URL = "mysql+pymysql://root:@127.0.0.1/bd_anuncios?charset=utf8mb4"
$env:SECRET_KEY = "reemplaza-por-una-clave-aleatoria-larga"
$env:NOMBRE_INSTITUCION = "Nombre de tu institución"
flask --app iniciar.py crear-administrador
flask --app iniciar.py run
```

Si MySQL tiene contraseña, inclúyela en la URL y codifica los caracteres reservados. La configuración predeterminada guarda SQLite en `instance/bd_anuncios.sqlite`; `create_app()` crea las tablas si no existen.

El nombre que aparece en la cabecera se configura mediante `NOMBRE_INSTITUCION`. Si tienes una base SQLite creada por una versión anterior, la aplicación renombra automáticamente la columna `password_hash` a `contrasena_hash`.

## Estructura del proyecto

```text
app/
  autenticacion/
    formularios.py
    rutas.py
  anuncios/
    formularios.py
    rutas.py
  categorias/
    formularios.py
    rutas.py
  inicio/
    rutas.py
  usuarios/
    formularios.py
    rutas.py
  static/css/estilos.css
  templates/
    autenticacion/
    anuncios/
    categorias/
    inicio/
    usuarios/
    base.html
  __init__.py             Fábrica de la aplicación y configuración de extensiones
  modelos.py              Modelos y relaciones de la base de datos
configuracion.py           Configuración de la aplicación
iniciar.py                 Punto de entrada de Flask
schema.sql                 Esquema MySQL/MariaDB de bd_anuncios
tests/test_app.py          Pruebas automatizadas
docs/                      Informe PDF, capturas y generador del informe
```

## Modelo de datos

- `usuarios` (1) — (N) `anuncios`: cada publicación pertenece a un usuario.
- `categorias` (1) — (N) `anuncios`: cada publicación pertenece a una categoría.
- `anuncios` requiere una categoría y un usuario. Las claves foráneas restringen la eliminación de registros relacionados.
- El hash de contraseña se guarda en `contrasena_hash`; nunca se almacena la contraseña en texto claro.

## Pruebas

```powershell
python -m pytest
```

## Informe y repositorio

El informe se genera con:

```powershell
python docs\generar_informe.py
```

El generador incorpora las capturas PNG de `docs/capturas/`.

Repositorio: <https://github.com/brayanzuniga044/actividad4-tablon-anuncios>
