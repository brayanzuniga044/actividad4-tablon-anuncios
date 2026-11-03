# Actividad N.º 4 — Tablón de Anuncios con Flask

Aplicación web modular para publicar y administrar anuncios institucionales. Está construida con Flask, SQLAlchemy, Flask-Login, formularios protegidos contra CSRF y Bootstrap 5.

## Funcionalidades

- Inicio público con búsqueda de texto y filtro por categoría.
- Inicio de sesión por nombre de usuario o correo; contraseñas almacenadas con hash.
- Administración autenticada: altas, consultas, modificaciones y bajas de usuarios, categorías y anuncios.
- Cada anuncio queda relacionado con una categoría y un usuario.
- Las categorías o usuarios con anuncios asociados no se pueden borrar; tampoco se puede borrar la cuenta con sesión activa.
- Diseño adaptable a móvil y páginas con cabecera, menú y pie comunes.
- Patrón Application Factory (`create_app`) y Blueprints por módulo.
- SQLite como opción lista para ejecutar; conexión configurable para MySQL/MariaDB de XAMPP.

## Requisitos

- Python 3.10 o posterior.
- Para usar MySQL: MySQL/MariaDB iniciado (por ejemplo, desde el panel de XAMPP).

## Instalación y ejecución

Desde la carpeta del proyecto, en PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
flask --app run.py init-db
flask --app run.py create-admin
flask --app run.py run
```

Abre <http://127.0.0.1:5000/>. El comando `create-admin` solicita nombre, correo, usuario y contraseña; no hay credenciales administrativas predeterminadas.

### Conectar con MySQL/MariaDB (XAMPP)

1. Inicia MySQL desde XAMPP.
2. En phpMyAdmin importa [`schema.sql`](./schema.sql), que crea `bd_anuncios` y las tablas relacionales.
3. En PowerShell define la conexión antes de iniciar Flask:

```powershell
$env:DATABASE_URL = "mysql+pymysql://root:@127.0.0.1/bd_anuncios?charset=utf8mb4"
$env:SECRET_KEY = "reemplaza-por-una-clave-aleatoria-larga"
$env:INSTITUTION_NAME = "Nombre de tu institución"
flask --app run.py create-admin
flask --app run.py run
```

Si MySQL tiene contraseña, inclúyela en la URL (codifica caracteres reservados). La URL de SQLite por defecto guarda la base de datos en `instance/bd_anuncios.sqlite`. `create_app()` crea las tablas si todavía no existen.

El nombre institucional de la cabecera se configura mediante `INSTITUTION_NAME`; el valor predeterminado es «Institución Educativa».

## Estructura del proyecto

```text
app/
  announcements/       Rutas y formulario de anuncios
  auth/                Inicio y cierre de sesión
  categories/          Rutas y formulario de categorías
  main/                Portada y filtros
  users/               Rutas y formulario de usuarios
  static/css/          Estilos propios
  templates/           Plantilla común y vistas por módulo
  __init__.py           create_app, extensiones y comandos CLI
  models.py             Modelos y relaciones SQLAlchemy
config.py               Configuración por variables de entorno
run.py                  Punto de entrada
schema.sql              Esquema MySQL/MariaDB para bd_anuncios
tests/                  Pruebas automatizadas
docs/                   Informe PDF y capturas
```

## Modelo de datos

- `usuarios` (1) — (N) `anuncios`: cada publicación pertenece a un usuario.
- `categorias` (1) — (N) `anuncios`: cada publicación pertenece a una categoría.
- `anuncios` no permite eliminar la categoría o el usuario referenciados; primero se deben eliminar o reasignar sus publicaciones.
- Los campos equivalentes en los modelos SQLAlchemy se mapean a nombres españoles en la base de datos. El esquema y la base SQLite comparten las tablas `usuarios`, `categorias` y `anuncios`.

## Pruebas

```powershell
python -m pytest
```

## Informe PDF y repositorio

El informe requerido se genera con:

```powershell
python docs\generar_informe.py
```

El generador incorpora las imágenes que encuentre en `docs/capturas/`. El proyecto incluye capturas de las pantallas funcionales. El enlace GitHub debe añadirse una vez que el titular publique este código en su cuenta; no se incluye un enlace ficticio ni se publican archivos automáticamente.
