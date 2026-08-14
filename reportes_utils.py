import pandas as pd
from tkinter import filedialog, messagebox
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import TableStyle
from config_sistema import obtener_config
from datetime import datetime
import os
import sys
from core import *
from reportlab.lib.units import mm
from tkinter import filedialog


def limpiar_numero(valor):
    try:
        v = str(valor).strip()

        if v == "" or v.lower() == "none":
            return None

        # reemplazar coma decimal por punto
        v = v.replace(".", "").replace(",", ".")

        return float(v)
    except:
        return None


################################
# detectar si celda es numero
def es_numero(valor):
    try:
        float(str(valor).replace(",", ""))
        return True
    except:
        return False


ANCHO_COLUMNAS = {
    "KARDEX": [70, 80, 260, 70, 50, 50],
    "KARDEX GENERAL": [70, 80, 260, 70, 50, 50],
    "KARDEX TOTAL": [80, 260, 70, 70, 70],
    "INVENTARIO VALORIZADO": [70, 260, 40, 80, 80],
}


def generar_reporte_pdf(tree, titulo):

    total_registros = len(tree.get_children())

    if titulo is None:
        titulo = getattr(tree, "reporte_titulo", "REPORTE")

    archivo = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=f"{titulo.replace(' ', '_')}.pdf",
    )

    if not archivo:
        return

    estilos = getSampleStyleSheet()
    elementos = []

    # ===== COLUMNAS =====
    columnas = [c.replace("_", " ").upper() for c in tree["columns"]]

    datos = [columnas]
    filas_originales = []

    # ===== CARGAR DATOS =====
    for row in tree.get_children():
        valores = list(tree.item(row)["values"])

        # quitar hora a fechas
        for i, v in enumerate(valores):
            if isinstance(v, str) and " " in v and ":" in v:
                valores[i] = v.split(" ")[0]

        filas_originales.append(valores)
        datos.append(valores)

        # ===== TOTALES AUTOMÁTICOS =====
    totales = [""] * len(columnas)
    titulo_upper = str(titulo).strip().upper()
    
    if titulo_upper in ("KARDEX", "KARDEX GENERAL", "KARDEX TOTAL"):
        totales[0] = "TOTAL"

        # Sumar únicamente Entradas y Salidas
        for col in range(len(columnas)):
            nombre = columnas[col].lower().strip()

            if "entrada" in nombre or "salida" in nombre:
                suma = 0

                for fila in filas_originales:
                    if col >= len(fila):
                        continue

                    valor = str(fila[col]).replace(",", "").strip()

                    if valor == "":
                        continue

                    try:
                        suma += float(valor)
                    except:
                        continue

                totales[col] = f"{suma:,.2f}"

        # Colocar el saldo final (último saldo del kardex)
        if filas_originales:
            totales[-1] = filas_originales[-1][-1]

        datos.append(totales)

    else:
        for col in range(len(columnas)):
            nombre = columnas[col].lower()

            # no sumar campos numéricos que realmente son identificaciones o teléfonos
            if (
                "codigo" in nombre
                or "id" in nombre
                or "telefono" in nombre
                or "teléfono" in nombre
                or "celular" in nombre
                or "movil" in nombre
                or "móvil" in nombre
                or "cedula" in nombre
                or "cédula" in nombre
                or "rif" in nombre
                or "documento" in nombre
            ):
                continue

            suma = 0
            tiene_numeros = False

            for fila in filas_originales:
                if col >= len(fila):
                    continue

                valor = str(fila[col]).replace(",", "").strip()

                if valor == "":
                    continue

                try:
                    suma += float(valor)
                    tiene_numeros = True
                except:
                    continue

            if tiene_numeros:
                totales[col] = f"{suma:,.2f}"

        if any(str(v).strip() != "" for v in totales):
            totales[0] = "TOTAL"
            datos.append(totales)

    # ===== TOTAL GENERAL =====
    

    total_general = None
    if titulo_upper not in ("KARDEX", "KARDEX GENERAL", "KARDEX TOTAL"):
        suma = 0
        tiene_numeros = False

        if len(columnas) > 0:
            ultima = len(columnas) - 1

            for fila in filas_originales:
                if ultima >= len(fila):
                    continue

                valor = str(fila[ultima]).replace(",", "").strip()
                if valor == "":
                    continue

                try:
                    suma += float(valor)
                    tiene_numeros = True
                except:
                    continue

        if tiene_numeros:
            total_general = suma

    # ===== ORIENTACIÓN AUTOMÁTICA =====
    num_cols = len(columnas)

    if num_cols > 6:
        pagesize = landscape(letter)
    else:
        pagesize = letter

    doc = SimpleDocTemplate(
        archivo,
        pagesize=pagesize,
        rightMargin=20,
        leftMargin=20,
        topMargin=90,
        bottomMargin=50,
    )

    doc.titulo_reporte = titulo

    # ===== ANCHO COLUMNAS =====
    ancho_total = doc.width

    if titulo_upper in ANCHO_COLUMNAS:
        col_widths = ANCHO_COLUMNAS[titulo_upper]
    else:
        tamaños = []

        for col in range(len(columnas)):
            max_len = len(str(columnas[col]))

            for fila in filas_originales:
                if col >= len(fila):
                    continue
                largo = len(str(fila[col]))
                if largo > max_len:
                    max_len = largo

            tamaños.append(max_len)

        suma = sum(tamaños)
        col_widths = [(ancho_total * (t / suma)) for t in tamaños]
        col_widths = [max(50, w) for w in col_widths]

    # ===== TABLA =====
    tabla = Table(datos, colWidths=col_widths, repeatRows=1)

    # ===== ESTILO TABLA =====
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTSIZE", (0, 1), (-1, -2), 8),  # cuerpo
        ("FONTSIZE", (0, -1), (-1, -1), 9),  # fila total
    ]

    # ===== ALINEACIÓN NUMÉRICA =====
    for col in range(len(columnas)):
        nombre = columnas[col].lower()

        if (
            "entrada" in nombre
            or "salida" in nombre
            or "cantidad" in nombre
            or "precio" in nombre
            or "costo" in nombre
            or "total" in nombre
            or "saldo" in nombre
            or "stock" in nombre
            or "existencia" in nombre
            or "valor" in nombre
        ):
            estilo.append(("ALIGN", (col, 1), (col, -1), "RIGHT"))
            continue

        es_num = True

        for fila in filas_originales:
            if col >= len(fila):
                continue

            valor = str(fila[col]).strip()

            if valor == "":
                continue

            try:
                float(valor.replace(",", ""))
            except:
                es_num = False
                break

        if es_num:
            estilo.append(("ALIGN", (col, 1), (col, -1), "RIGHT"))
        else:
            estilo.append(("ALIGN", (col, 1), (col, -1), "LEFT"))

    tabla.setStyle(TableStyle(estilo))

    elementos.append(tabla)
    elementos.append(Spacer(1, 20))

    # ===== RESUMEN =====
    elementos.append(
        Paragraph(f"<b>Total registros:</b> {total_registros}", estilos["Normal"])
    )

    if total_general is not None:
        elementos.append(
            Paragraph(f"<b>Total general:</b> {total_general:,.2f}", estilos["Normal"])
        )

    # ===== GENERAR PDF =====
    doc.build(
        elementos,
        onFirstPage=dibujar_encabezado_pie,
        onLaterPages=dibujar_encabezado_pie,
    )

    if sys.platform == "win32":
        os.startfile(archivo)


#################################################
def exportar_excel(tree, titulo="REPORTE"):

    columnas = tree["columns"]

    datos = []

    for row in tree.get_children():
        datos.append(tree.item(row)["values"])

    if not datos:
        messagebox.showwarning("Excel", "No hay datos para exportar")
        return

    archivo = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        initialfile=f"{titulo}.xlsx",
    )

    if not archivo:
        return

    df = pd.DataFrame(datos, columns=columnas)

    # limpiar números
    for col in df.columns:
        df[col] = df[col].apply(
            lambda x: float(str(x).replace(",", "")) if es_numero(x) else x
        )

    try:

        with pd.ExcelWriter(archivo, engine="xlsxwriter") as writer:

            df.to_excel(writer, sheet_name="Reporte", index=False, startrow=5)

            workbook = writer.book
            worksheet = writer.sheets["Reporte"]

            empresa = "WSoft"
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

            # ===== FORMATOS =====

            formato_empresa = workbook.add_format({"bold": True, "font_size": 14})
            formato_titulo = workbook.add_format({"bold": True, "font_size": 12})
            formato_fecha = workbook.add_format({"italic": True})

            formato_header = workbook.add_format(
                {
                    "bold": True,
                    "bg_color": "#1f4e78",
                    "font_color": "white",
                    "align": "center",
                }
            )

            formato_numero = workbook.add_format({"num_format": "#,##0.00"})
            formato_total = workbook.add_format(
                {"bold": True, "num_format": "#,##0.00"}
            )

            formato_total_texto = workbook.add_format({"bold": True})

            # ===== ENCABEZADO =====

            worksheet.write("A1", empresa, formato_empresa)
            worksheet.write("A2", titulo, formato_titulo)
            worksheet.write("A3", f"Fecha: {fecha}", formato_fecha)

            # ===== CABECERAS DE TABLA =====

            for col_num, col_name in enumerate(df.columns):
                worksheet.write(5, col_num, col_name, formato_header)

            # ===== AJUSTAR COLUMNAS =====

            for i, col in enumerate(df.columns):

                nombre_col = col.lower()

                ancho = max(df[col].astype(str).map(len).max(), len(col)) + 2

                if "codigo" in nombre_col or "id" in nombre_col:
                    worksheet.set_column(i, i, ancho)

                elif pd.api.types.is_numeric_dtype(df[col]):
                    worksheet.set_column(i, i, ancho, formato_numero)

                else:
                    worksheet.set_column(i, i, ancho)

            # ===== FILTROS =====

            worksheet.autofilter(5, 0, 5 + len(df), len(df.columns) - 1)

            # ===== CONGELAR ENCABEZADO =====

            worksheet.freeze_panes(6, 0)

            # ===== TOTAL AUTOMÁTICO =====

            fila_total = len(df) + 6

            worksheet.write(fila_total, 0, "TOTAL", formato_total_texto)

            for col in range(len(df.columns)):

                nombre_col = df.columns[col].lower()

                if (
                    pd.api.types.is_numeric_dtype(df.iloc[:, col])
                    and "codigo" not in nombre_col
                    and "id" not in nombre_col
                ):

                    letra = chr(65 + col)

                    formula = f"=SUM({letra}7:{letra}{len(df)+6})"

                    worksheet.write_formula(fila_total, col, formula, formato_total)

        messagebox.showinfo("Excel", "Reporte exportado correctamente")

        if sys.platform == "win32":
            os.startfile(archivo)

    except Exception as e:
        messagebox.showerror("Excel", f"No se pudo exportar:\n{e}")


##########################################################
def crear_botones_reporte(frame, tree, titulo="REPORTE"):

    from reportes_utils import generar_reporte_pdf

    # Frame de botones
    frame_btn = ctk.CTkFrame(frame, fg_color="transparent")
    frame_btn.pack(fill="x", pady=5)

    # BOTON PDF
    btn_pdf = ctk.CTkButton(
        frame_btn,
        text="📄 PDF",
        width=120,
        command=lambda: generar_reporte_pdf(tree, titulo),
    )
    btn_pdf.pack(side="left", padx=5)

    # BOTON EXCEL
    btn_excel = ctk.CTkButton(
        frame_btn,
        text="📊 Excel",
        width=120,
        command=lambda: exportar_excel(tree, titulo),
    )
    btn_excel.pack(side="left", padx=5)


######################################
def dibujar_encabezado_pie(canvas, doc):

    config = obtener_config()
    empresa = config["empresa"]
    sistema = config["sistema"]
    titulo = getattr(doc, "titulo_reporte", "")

    canvas.saveState()

    ancho, alto = doc.pagesize
    fecha = datetime.now().strftime("%d/%m/%Y")

    # ---- ENCABEZADO ----
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(20 * mm, alto - 18 * mm, empresa)

    canvas.setFont("Helvetica", 9)
    canvas.drawString(20 * mm, alto - 24 * mm, sistema)

    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(ancho - 20 * mm, alto - 18 * mm, f"Fecha: {fecha}")

    # título centrado
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawCentredString(ancho / 2, alto - 32 * mm, titulo)

    # línea debajo del título
    canvas.line(20 * mm, alto - 36 * mm, ancho - 20 * mm, alto - 36 * mm)

    # ---- PIE ----
    texto = f"Generado por WSoft | Página {doc.page}"

    canvas.line(20 * mm, 15 * mm, ancho - 20 * mm, 15 * mm)

    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(ancho / 2, 10 * mm, texto)

    canvas.restoreState()
