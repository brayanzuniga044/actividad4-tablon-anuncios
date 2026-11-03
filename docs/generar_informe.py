from pathlib import Path
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "actividad4.pdf"
SCREENSHOTS = ROOT / "docs" / "capturas"
NAVY = colors.HexColor("#122541")
BLUE = colors.HexColor("#2457a7")
PALE = colors.HexColor("#edf3fb")
INSTITUTION = os.environ.get("NOMBRE_INSTITUCION", "Institución Educativa")


def build_report():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold",
                              fontSize=26, leading=31, textColor=NAVY, alignment=TA_CENTER, spaceAfter=12))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading1"], fontName="Helvetica-Bold",
                              fontSize=17, leading=21, textColor=NAVY, spaceBefore=10, spaceAfter=8))
    styles.add(ParagraphStyle(name="Subsection", parent=styles["Heading2"], fontSize=12,
                              textColor=BLUE, spaceBefore=7, spaceAfter=5))
    styles.add(ParagraphStyle(name="BodySmall", parent=styles["BodyText"], fontSize=9,
                              leading=13, spaceAfter=6))
    styles.add(ParagraphStyle(name="Caption", parent=styles["BodyText"], fontSize=8,
                              textColor=colors.HexColor("#5f6e80"), alignment=TA_CENTER, spaceAfter=10))
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title="Actividad 4 - Tablón de Anuncios con Flask",
        author=INSTITUTION,
    )
    story = [
        Spacer(1, 23 * mm),
        Paragraph("ACTIVIDAD N.º 4", styles["CoverTitle"]),
        Paragraph("Tablón de Anuncios con Flask", styles["Heading2"]),
        Spacer(1, 8 * mm),
        Paragraph("Aplicación web para la gestión de usuarios, categorías y anuncios institucionales.",
                  styles["BodyText"]),
        Spacer(1, 8 * mm),
        Paragraph(f"<b>Institución:</b> {INSTITUTION}", styles["BodyText"]),
        Paragraph("<b>Tecnologías:</b> Python, Flask, SQLAlchemy, SQLite/MySQL y Bootstrap 5", styles["BodyText"]),
        Paragraph("<b>Arquitectura:</b> Application Factory y Blueprints", styles["BodyText"]),
        Spacer(1, 28 * mm),
        Paragraph("Documento de diseño y evidencia de funcionamiento", styles["Caption"]),
        PageBreak(),
        Paragraph("1. Diseño de base de datos", styles["Section"]),
        Paragraph("La aplicación utiliza una base de datos relacional denominada <b>bd_anuncios</b>. "
                  "Los modelos SQLAlchemy crean las tablas al iniciar la aplicación. El archivo "
                  "<b>schema.sql</b> contiene el DDL para MySQL/MariaDB.", styles["BodySmall"]),
        Paragraph("Tablas", styles["Subsection"]),
    ]
    table_data = [
        ["Tabla", "Campos principales", "Claves y restricciones"],
        ["usuarios", "id, nombre, correo, nombre_usuario, contrasena_hash, creado_en",
         "PK: id · UNIQUE: correo, nombre_usuario"],
        ["categorias", "id, nombre, descripcion",
         "PK: id · UNIQUE: nombre"],
        ["anuncios", "id, titulo, contenido, creado_en, categoria_id, usuario_id",
         "PK: id · FK categoria_id → categorias.id · FK usuario_id → usuarios.id"],
    ]
    table = Table(table_data, colWidths=[26 * mm, 72 * mm, 66 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#dce3ec")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story += [
        table, Spacer(1, 4 * mm),
        Paragraph("Relaciones", styles["Subsection"]),
        Paragraph("• usuarios (1) — (N) anuncios: un usuario puede publicar varios anuncios.<br/>"
                  "• categorias (1) — (N) anuncios: una categoría puede agrupar varios anuncios.<br/>"
                  "• Cada anuncio requiere una categoría y un usuario. Las claves foráneas restringen "
                  "la eliminación de registros referenciados.", styles["BodySmall"]),
        Paragraph("Diagrama entidad-relación", styles["Subsection"]),
        Paragraph("<font name='Courier'>USUARIOS (1) ────────&lt; (N) ANUNCIOS (N) &gt;──────── (1) CATEGORIAS</font>",
                  styles["BodySmall"]),
        Paragraph("2. Estructura y arquitectura", styles["Section"]),
        Paragraph("La función create_app() inicializa extensiones, configuración y base de datos. "
                  "Cada área funcional está aislada en un Blueprint. Los modelos centralizan las "
                  "relaciones y las vistas comparten una plantilla institucional común.", styles["BodySmall"]),
    ]
    structure = [
        ["Módulo", "Responsabilidad"],
        ["app/autenticacion", "Inicio de sesión y cierre de sesión"],
        ["app/usuarios", "Administración de usuarios"],
        ["app/categorias", "Administración de categorías"],
        ["app/anuncios", "Administración de anuncios"],
        ["app/inicio", "Portada pública, búsqueda y filtros"],
        ["app/modelos.py", "Modelos y relaciones SQLAlchemy"],
        ["app/templates + app/static", "Vistas HTML comunes y estilos Bootstrap"],
        ["configuracion.py / iniciar.py / schema.sql", "Configuración, punto de entrada y esquema MySQL"],
    ]
    st = Table(structure, colWidths=[55 * mm, 109 * mm], repeatRows=1)
    st.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#dce3ec")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [st, PageBreak(), Paragraph("3. Capturas de funcionamiento", styles["Section"])]
    images = sorted(SCREENSHOTS.glob("*.png")) if SCREENSHOTS.exists() else []
    if images:
        for image_path in images:
            image = Image(str(image_path), width=165 * mm, height=92 * mm, kind="proportional")
            story.append(KeepTogether([
                Paragraph(image_path.stem.replace("_", " ").title(), styles["Subsection"]),
                image,
                Paragraph(f"Captura de pantalla: {image_path.name}", styles["Caption"]),
            ]))
    else:
        story.append(Paragraph(
            "No se encontraron capturas. Guarda imágenes PNG de la aplicación en docs/capturas/ "
            "y vuelve a ejecutar este generador.", styles["BodySmall"]
        ))
    story += [
        Spacer(1, 8 * mm),
        Paragraph("4. Ejecución", styles["Section"]),
        Paragraph("Instalar dependencias con <b>pip install -r requirements.txt</b>, crear la cuenta "
                  "inicial con <b>flask --app iniciar.py crear-administrador</b> e iniciar con "
                  "<b>flask --app iniciar.py run</b>. La configuración predeterminada utiliza SQLite; "
                  "DATABASE_URL permite conectar MySQL/MariaDB.", styles["BodySmall"]),
        Paragraph(
            'Repositorio GitHub: <link href="https://github.com/brayanzuniga044/actividad4-tablon-anuncios" '
            'color="blue">github.com/brayanzuniga044/actividad4-tablon-anuncios</link>.',
            styles["BodySmall"],
        ),
    ]

    def page_footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#dce3ec"))
        canvas.line(20 * mm, 13 * mm, A4[0] - 20 * mm, 13 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#6f7e90"))
        canvas.drawString(20 * mm, 8 * mm, f"{INSTITUTION} · Actividad N.º 4")
        canvas.drawRightString(A4[0] - 20 * mm, 8 * mm, f"Página {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    print(f"Informe generado: {OUTPUT}")


if __name__ == "__main__":
    build_report()
