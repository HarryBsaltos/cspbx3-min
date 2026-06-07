#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera el informe del trabajo final del curso HCC en PDF."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)

HERE = Path(__file__).resolve().parent
FIGS = HERE / "figs"
OUT = HERE / "informe_HCC.pdf"


def build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="TitleES",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=18,
    ))
    styles.add(ParagraphStyle(
        name="H1",
        parent=styles["Heading1"],
        fontSize=14,
        leading=18,
        spaceBefore=14,
        spaceAfter=8,
        textColor=colors.HexColor("#1a3a6c"),
    ))
    styles.add(ParagraphStyle(
        name="H2",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        spaceBefore=8,
        spaceAfter=4,
        textColor=colors.HexColor("#1a3a6c"),
    ))
    styles.add(ParagraphStyle(
        name="Body",
        parent=styles["Normal"],
        fontSize=10.5,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="Caption",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name="Ref",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=12,
        alignment=TA_LEFT,
        leftIndent=18,
        firstLineIndent=-18,
        spaceAfter=4,
    ))
    return styles


def fig(path: Path, width=14 * cm) -> Image:
    img = Image(str(path))
    ratio = img.imageHeight / img.imageWidth
    img.drawWidth = width
    img.drawHeight = width * ratio
    return img


def main():
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.0 * cm,
        title="Trabajo final HCC — Mínimo de la superficie de energía DFT de CsPbX3",
        author="Trabajo final del curso HCC",
    )

    s = build_styles()
    story = []

    # ---------------- Portada / Encabezado ----------------
    story.append(Paragraph(
        "Búsqueda del mínimo de la superficie de energía DFT en perovskitas CsPbX<sub>3</sub>",
        s["TitleES"],
    ))
    story.append(Paragraph(
        "Trabajo final &mdash; Curso <i>Herramientas Computacionales para Cient&iacute;ficos</i> (HCC)",
        s["Subtitle"],
    ))

    # ---------------- 1. Introducción ----------------
    story.append(Paragraph("1. Introducción", s["H1"]))
    story.append(Paragraph(
        "Las perovskitas de haluro de cesio y plomo, de fórmula general "
        "CsPbX<sub>3</sub> con X = Cl, Br o I, constituyen una familia de "
        "semiconductores que ha despertado un fuerte interés tecnológico en "
        "la última década por su uso en celdas solares de alta eficiencia, "
        "diodos emisores de luz y detectores de radiación. Sus propiedades "
        "ópticas y electrónicas dependen de manera muy sensible de la "
        "estructura cristalina y, en particular, de la rotación cooperativa "
        "de los octaedros [PbX<sub>6</sub>] dentro de la celda unidad. "
        "Caracterizar esa rotación es por lo tanto una tarea central a la "
        "hora de modelar la fase estable a una dada temperatura.",
        s["Body"],
    ))
    story.append(Paragraph(
        "El presente trabajo aborda el problema de localizar la "
        "configuración de equilibrio del compuesto CsPbBr<sub>3</sub> a "
        "partir de una superficie de energía 2D obtenida por cálculos de "
        "<i>primeros principios</i> dentro del marco de la teoría del "
        "funcional de la densidad (DFT). La superficie está muestreada "
        "sobre una grilla de 21&times;21 puntos correspondientes a dos "
        "ángulos de rotación (θ, φ) de los octaedros [PbBr<sub>6</sub>]; "
        "para cada par de ángulos se conoce la energía total E(θ, φ).",
        s["Body"],
    ))
    story.append(Paragraph(
        "El programa <font face=\"Courier\">cspbx3_min.py</font> "
        "automatiza tres tareas: (i) la lectura y visualización de la "
        "superficie completa, (ii) la selección de una sub-región alrededor "
        "del mínimo discreto y (iii) la determinación del mínimo continuo "
        "mediante interpolación spline bicúbica. El mismo flujo es aplicable "
        "a las tres composiciones (X = Cl, Br, I) sin más que cambiar el "
        "archivo de entrada.",
        s["Body"],
    ))

    # ---------------- 2. Herramientas computacionales ----------------
    story.append(Paragraph("2. Herramientas computacionales", s["H1"]))

    story.append(Paragraph("2.1. Lenguaje y ecosistema", s["H2"]))
    story.append(Paragraph(
        "El programa está escrito íntegramente en <b>Python 3</b> por su "
        "expresividad, su disponibilidad transversal en sistemas operativos "
        "Unix y por contar con una pila científica madura. Se utilizan "
        "exclusivamente bibliotecas libres y multiplataforma:",
        s["Body"],
    ))
    libs_data = [
        ["Biblioteca", "Versión mínima", "Función en el código"],
        ["NumPy", "1.20+", "Lectura del archivo, manipulación de la grilla 2D, búsqueda del mínimo discreto."],
        ["SciPy", "1.7+", "Interpolación bicúbica mediante RectBivariateSpline."],
        ["Matplotlib", "3.4+", "Graficación 3D de las superficies con barra de color."],
        ["argparse", "stdlib", "Interfaz de línea de comandos con paths configurables."],
    ]
    libs_table = Table(libs_data, colWidths=[3.2 * cm, 2.8 * cm, 9.5 * cm])
    libs_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3a6c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f4f7fb")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(libs_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("2.2. Origen de los datos", s["H2"]))
    story.append(Paragraph(
        "El archivo de entrada <font face=\"Courier\">CsPbBr3_AA_AA.txt</font> "
        "contiene 441 filas con tres columnas: índice θ, índice φ y energía "
        "total <i>E</i>(θ, φ) calculada por DFT. Las energías están dadas en "
        "las unidades nativas del código DFT empleado (típicamente eV o "
        "Ry). Las dos primeras columnas son enteros entre 0 y 20, lo que "
        "define una grilla regular 21&times;21 sobre el espacio de ángulos "
        "de rotación reducidos al sub-espacio de simetría del grupo "
        "espacial de la fase considerada.",
        s["Body"],
    ))

    story.append(Paragraph("2.3. Algoritmo: interpolación spline bicúbica", s["H2"]))
    story.append(Paragraph(
        "Como la grilla DFT es discreta, el mínimo de la energía obtenido "
        "directamente de la matriz 21&times;21 está sesgado por el paso de "
        "muestreo. Para refinar la posición del mínimo se recurre a una "
        "interpolación bidimensional con splines bicúbicos, implementada "
        "en SciPy mediante la clase "
        "<font face=\"Courier\">RectBivariateSpline</font>. El spline "
        "bicúbico construye un polinomio a trozos de grado 3 en cada "
        "variable, garantizando continuidad de la función y de sus "
        "primeras derivadas en las uniones; es por lo tanto adecuado "
        "para representar la curvatura de un pozo de energía cerca del "
        "equilibrio.",
        s["Body"],
    ))
    story.append(Paragraph(
        "Por eficiencia y para evitar oscilaciones espurias, la "
        "interpolación se restringe a una sub-región de 5&times;5 puntos "
        "que contiene al mínimo discreto. Sobre esa sub-región se "
        "construye una malla refinada con paso 0,1 (una décima parte del "
        "paso de la grilla DFT) y se localiza el mínimo continuo por "
        "búsqueda directa con <font face=\"Courier\">np.argmin</font> "
        "sobre el array interpolado.",
        s["Body"],
    ))

    story.append(Paragraph("2.4. Buenas prácticas de software aplicadas", s["H2"]))
    story.append(Paragraph(
        "El código respeta la convención <b>PEP 8</b> y agrega: "
        "<i>docstrings</i> con formato NumPy en cada función, "
        "<i>type hints</i>, separación clara entre lógica de cálculo y "
        "graficación, una interfaz de línea de comandos basada en "
        "<font face=\"Courier\">argparse</font> que permite cambiar el "
        "archivo de entrada y el directorio de salida sin editar el "
        "fuente, y selección automática del backend "
        "<font face=\"Courier\">Agg</font> de Matplotlib cuando no hay "
        "<font face=\"Courier\">$DISPLAY</font> (lo que lo hace "
        "directamente ejecutable en una terminal Linux remota o en un "
        "entorno de integración continua).",
        s["Body"],
    ))

    # ---------------- 3. Resultados ----------------
    story.append(PageBreak())
    story.append(Paragraph("3. Resultados", s["H1"]))

    story.append(Paragraph("3.1. Superficie de energía completa", s["H2"]))
    story.append(Paragraph(
        "La Figura 1 muestra la superficie de energía relativa al mínimo "
        "discreto, expresada en meV, sobre la grilla 21&times;21 completa. "
        "Se aprecia un pozo bien definido en la región central baja del "
        "plano (θ, φ) y un crecimiento abrupto de la energía hacia la "
        "esquina (θ&nbsp;=&nbsp;20, φ&nbsp;=&nbsp;20), en la que la "
        "configuración pierde estabilidad por la deformación excesiva de "
        "los octaedros.",
        s["Body"],
    ))
    story.append(KeepTogether([
        fig(FIGS / "01_surface_full.png", width=12.5 * cm),
        Paragraph(
            "Figura 1. Superficie de energía DFT completa (21&times;21) de "
            "CsPbBr<sub>3</sub>, expresada en meV respecto del mínimo "
            "discreto.",
            s["Caption"],
        ),
    ]))

    story.append(Paragraph("3.2. Sub-región e interpolación", s["H2"]))
    story.append(Paragraph(
        "La inspección visual de la Figura 1 indica que el mínimo se "
        "localiza dentro del rectángulo definido por θ ∈ [0, 4] y "
        "φ ∈ [9, 13]. La Figura 2 muestra esa sub-región original de "
        "5&times;5 puntos, donde el pozo se ve resuelto con detalle. La "
        "Figura 3 muestra la misma región luego de la interpolación "
        "bicúbica, sobre una malla refinada con paso 0,1.",
        s["Body"],
    ))
    story.append(KeepTogether([
        fig(FIGS / "02_surface_sub.png", width=12.0 * cm),
        Paragraph(
            "Figura 2. Sub-región 5&times;5 alrededor del mínimo discreto.",
            s["Caption"],
        ),
    ]))
    story.append(KeepTogether([
        fig(FIGS / "03_surface_spline.png", width=12.0 * cm),
        Paragraph(
            "Figura 3. Sub-región tras la interpolación spline bicúbica.",
            s["Caption"],
        ),
    ]))

    story.append(Paragraph("3.3. Mínimo continuo", s["H2"]))
    story.append(Paragraph(
        "La Tabla 2 resume los valores numéricos obtenidos al ejecutar el "
        "programa sobre el archivo <font face=\"Courier\">"
        "CsPbBr3_AA_AA.txt</font>. La energía absoluta E<sub>0</sub> se "
        "reconstruye sumando al mínimo continuo (en meV, dividido por "
        "1000) el mínimo discreto E<sub>min</sub> que se restó en el "
        "preprocesamiento.",
        s["Body"],
    ))
    res_data = [
        ["Magnitud", "Valor"],
        ["Mínimo discreto E_min", "−127,843510 (unid. orig.)"],
        ["Mínimo interpolado (relativo)", "−0,0100 meV"],
        ["Energía absoluta E₀", "−127,843520 (unid. orig.)"],
        ["θ* (índice de la grilla)", "1,900"],
        ["φ* (índice de la grilla)", "11,000"],
    ]
    res_table = Table(res_data, colWidths=[7.5 * cm, 6.5 * cm])
    res_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3a6c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#f4f7fb"), colors.white]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(res_table)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Tabla 2. Valores reportados por el programa al ejecutarse sobre "
        "el archivo de CsPbBr<sub>3</sub>.",
        s["Caption"],
    ))
    story.append(Paragraph(
        "El refinamiento entrega una corrección menor que 0,02 meV "
        "respecto del mínimo discreto, lo que indica que la grilla "
        "original ya estaba muy cerca del mínimo verdadero del modelo. "
        "Aún así, la interpolación es indispensable para obtener una "
        "estimación continua de los ángulos (θ*, φ*) sin sesgo de "
        "muestreo, lo que es crítico cuando los datos provienen de un "
        "barrido más grueso. El valor obtenido θ*&nbsp;≈&nbsp;1,9 y "
        "φ*&nbsp;≈&nbsp;11,0 está dentro de la sub-región seleccionada, "
        "lo que confirma a posteriori que el recorte fue adecuado.",
        s["Body"],
    ))

    # ---------------- 4. Conclusiones ----------------
    story.append(Paragraph("4. Conclusiones", s["H1"]))
    story.append(Paragraph(
        "Se desarrolló un programa modular en Python para el "
        "post-procesamiento de superficies de energía DFT en perovskitas "
        "CsPbX<sub>3</sub>. El código separa explícitamente la lectura de "
        "datos, la interpolación y la graficación, está documentado según "
        "PEP 8, ofrece una interfaz por línea de comandos y se ejecuta sin "
        "modificaciones en cualquier sistema Linux con Python 3 y la pila "
        "científica estándar. El mismo programa puede aplicarse a las "
        "variantes con X = Cl, Br o I sin más que apuntar a otro archivo "
        "de entrada, por lo que constituye un punto de partida adecuado "
        "para un estudio sistemático de la familia.",
        s["Body"],
    ))

    # ---------------- 5. Bibliografía ----------------
    story.append(Paragraph("5. Bibliografía", s["H1"]))
    refs = [
        "[1] Hohenberg, P.; Kohn, W. <i>Inhomogeneous Electron Gas</i>. "
        "Physical Review, 136 (3B), B864–B871 (1964).",
        "[2] Kohn, W.; Sham, L. J. <i>Self-Consistent Equations Including "
        "Exchange and Correlation Effects</i>. Physical Review, 140 (4A), "
        "A1133–A1138 (1965).",
        "[3] Giannozzi, P. <i>et&nbsp;al.</i> <i>Quantum ESPRESSO: a "
        "modular and open-source software project for quantum simulations "
        "of materials</i>. J. Phys.: Condens. Matter 21, 395502 (2009).",
        "[4] Yaffe, O. <i>et&nbsp;al.</i> <i>Local Polar Fluctuations in "
        "Lead Halide Perovskite Crystals</i>. Physical Review Letters, "
        "118, 136001 (2017).",
        "[5] Beecher, A. N. <i>et&nbsp;al.</i> <i>Direct Observation of "
        "Dynamic Symmetry Breaking above Room Temperature in "
        "Methylammonium Lead Iodide Perovskite</i>. ACS Energy Letters, "
        "1, 880–887 (2016).",
        "[6] Harris, C. R. <i>et&nbsp;al.</i> <i>Array programming with "
        "NumPy</i>. Nature 585, 357–362 (2020).",
        "[7] Virtanen, P. <i>et&nbsp;al.</i> <i>SciPy 1.0: fundamental "
        "algorithms for scientific computing in Python</i>. Nature Methods "
        "17, 261–272 (2020).",
        "[8] Hunter, J. D. <i>Matplotlib: A 2D graphics environment</i>. "
        "Computing in Science &amp; Engineering, 9 (3), 90–95 (2007).",
        "[9] van Rossum, G.; Warsaw, B.; Coghlan, N. <i>PEP 8 — Style "
        "Guide for Python Code</i>. Python Enhancement Proposals, 2001.",
        "[10] de Boor, C. <i>A Practical Guide to Splines</i>, Applied "
        "Mathematical Sciences vol. 27, Springer, New York, 2001.",
    ]
    for r in refs:
        story.append(Paragraph(r, s["Ref"]))

    doc.build(story)
    print(f"PDF generado: {OUT}")


if __name__ == "__main__":
    main()
