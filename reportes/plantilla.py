from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
import os
import webbrowser
from core import *
from config import *
from reportes.utilidades import datos_empresa

def crear_documento(titulo, numero, cliente, items, archivo, subtotal=None, impuesto=0, total=None):

    empresa = datos_empresa()

    c = canvas.Canvas(archivo, pagesize=letter)

    width, height = letter

    y = height - 50


    # ==============================
    # LOGO
    # ==============================

    if empresa["logo"]:

        ruta_logo = os.path.join(
            LOGOS_DIR,
            empresa["logo"]
        )

        if os.path.exists(ruta_logo):
            #print("si pasa logoventa")

            c.drawImage(
                ruta_logo,
                50,
                y - 60,
                width=90,
                height=90
            )


    # ==============================
    # EMPRESA
    # ==============================

    c.setFont("Helvetica-Bold", 14)
    c.drawString(160, y, empresa["nombre"])

    y -= 18

    c.setFont("Helvetica", 10)
    c.drawString(160, y, empresa["direccion"])

    y -= 14

    c.drawString(
        160,
        y,
        f"Tel: {empresa['telefono']}"
    )


    # ==============================
    # TITULO
    # ==============================

    y -= 40

    c.setFont("Helvetica-Bold",16)

    c.drawCentredString(
        width/2,
        y,
        titulo
    )


    # ==============================
    # DATOS
    # ==============================

    y -= 30

    c.setFont("Helvetica",10)

    c.drawString(
        50,
        y,
        f"Documento N°: {numero:05d}"
    )

    c.drawRightString(
        550,
        y,
        f"Fecha: {datetime.now():%d/%m/%Y}"
    )


    if cliente:
        
        y -= 18
        
        
        if isinstance(cliente, dict):
            cliente_texto = cliente.get("nombre", "")
        else:
            cliente_texto = cliente


        c.drawString(
            50,
            y,
            f"Cliente: {cliente_texto}"
        )


    y -= 20

    c.line(50,y,550,y)


    # ==============================
    # CABECERA TABLA
    # ==============================

    y -= 20

    c.setFont("Helvetica-Bold",9)

    columnas = [
        (50,"COD"),
        (100,"PRODUCTO"),
        (330,"CANT"),
        (390,"PRECIO"),
        (440,"IVA"),
        (500,"IMP."),
        (550,"TOTAL")
    ]

    for x,texto in columnas:

        if x >= 330:
            c.drawRightString(x,y,texto)
        else:
            c.drawString(x,y,texto)


    y -= 8

    c.line(50,y,550,y)


    # ==============================
    # DETALLE
    # ==============================

    y -= 18

    c.setFont("Helvetica",9)

    for item in items:


        total_linea = (
            item["subtotal"] +
            item["impuesto_monto"]
        )


        c.drawString(
            50,
            y,
            str(item["codigo"])
        )

        c.drawString(
            100,
            y,
            item["descripcion"][:25]
        )


        c.drawRightString(
            330,
            y,
            str(item["cantidad"])
        )


        c.drawRightString(
            390,
            y,
            f"{item['precio']:,.2f}"
        )

        c.drawRightString(
            440,
            y,
            f"{item['impuesto']}%"
        )


        c.drawRightString(
            500,
            y,
            f"{item['impuesto_monto']:,.2f}"
        )


        c.drawRightString(
            550,
            y,
            f"{total_linea:,.2f}"
        )


        y -= 18



    # ==============================
    # TOTALES
    # ==============================

    y -= 10

    c.line(350,y,550,y)

    y -= 25

    c.setFont("Helvetica-Bold",13)


    c.drawRightString(
        550,
        y,
        f"SUBTOTAL: {subtotal:,.2f}"
    )


    y -= 18

    c.drawRightString(
        550,
        y,
        f"IMPUESTO: {impuesto:,.2f}"
    )


    y -= 18

    c.drawRightString(
        550,
        y,
        f"TOTAL: {total:,.2f}"
    )


    # ==============================
    # PIE
    # ==============================

    y -= 50

    c.setFont("Helvetica",9)

    c.drawCentredString(
        width/2,
        y,
        "Gracias por su compra"
    )


    c.save()

#    webbrowser.open_new(archivo)

#---------------------------
def crear_documentoc(titulo, numero, cliente, items, archivo):
    

    empresa = datos_empresa()

    c = canvas.Canvas(archivo, pagesize=letter)
    width, height = letter

    y = height - 50
    
    # ==============================
    # LOGO
    # ==============================

    if empresa["logo"]:

        ruta_logo = os.path.join(
            LOGOS_DIR,
            empresa["logo"]
        )

        if os.path.exists(ruta_logo):
            #print("si exite ruta")

            c.drawImage(
                ruta_logo,
                50,
                y - 60,
                width=90,
                height=90
            )

    # ===== DATOS EMPRESA =====
    c.setFont("Helvetica-Bold", 14)
    c.drawString(160, y, empresa["nombre"])

    y -= 18
    c.setFont("Helvetica", 10)
    c.drawString(160, y, empresa["direccion"])

    y -= 14
    c.drawString(160, y, f"Tel: {empresa['telefono']}")

    # ===== TITULO =====
    y -= 40
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y, titulo)

    # ===== INFO DOCUMENTO =====
    y -= 30
    c.setFont("Helvetica", 10)

    c.drawString(50, y, f"Documento N°: {numero:05d}")
    c.drawRightString(550, y, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")

    if cliente:
        y -= 18
        c.drawString(50, y, f" {cliente}")

    # ===== LINEA =====
    y -= 20
    c.line(50, y, 550, y)

    # ===== ENCABEZADO TABLA =====
    y -= 20
    c.setFont("Helvetica-Bold", 10)

    c.drawString(60, y, "COD")
    c.drawString(120, y, "PRODUCTO")
    c.drawRightString(380, y, "CANT")
    c.drawRightString(460, y, "PRECIO")
    c.drawRightString(550, y, "TOTAL")

    y -= 8
    c.line(50, y, 550, y)

    # ===== ITEMS =====
    y -= 18
    c.setFont("Helvetica", 10)

    total = 0

    for item in items:

        c.drawString(60, y, str(item["codigo"]))
        c.drawString(120, y, item["producto"])

        c.drawRightString(380, y, str(item["cantidad"]))
        c.drawRightString(460, y, f"{item['precio']:,.2f}")
        c.drawRightString(550, y, f"{item['total']:,.2f}")

        total += item["total"]

        y -= 18

    # ===== LINEA TOTAL =====
    y -= 10
    c.line(350, y, 550, y)

    # ===== TOTAL =====
    y -= 25
    c.setFont("Helvetica-Bold", 13)

    c.drawRightString(550, y, f"TOTAL: {total:,.2f}")

    # ===== PIE =====
    y -= 50
    c.setFont("Helvetica", 9)

    c.save()
