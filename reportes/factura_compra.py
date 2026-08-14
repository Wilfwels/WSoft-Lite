from reportes.plantilla import crear_documento
from reportes.utilidades import siguiente_numero


def factura_compra(provededores, carrito):

    numero = siguiente_numero("COMPRA")

    items = []

    for p in carrito:

        items.append(
            {
                "codigo": p["codigo"],
                "producto": p["nombre"],
                "cantidad": p["cantidad"],
                "precio": p["precio"],
                "total": p["cantidad"] * p["precio"],
            }
        )

    archivo = f"factura_{numero:05d}.pdf"

    crear_documento("FACTURA DE COMPRA", numero, provededores, items, archivo)


from reportes.plantilla import crear_documento
from reportes.utilidades import obtener_compra
import os


def factura_compra_id(id_compra):

    numero = id_compra
    archivo = f"documentos/facturas_compra/compra_{numero:05d}.pdf"

    # convertir a ruta absoluta
    archivo = os.path.abspath(archivo)

    # si existe abrir
    if os.path.exists(archivo):
        os.startfile(archivo)
        return

    proveedor, carrito = obtener_compra(id_compra)

    items = []

    for p in carrito:
        items.append(
            {
                "codigo": p["codigo"],
                "producto": p["descripcion"],
                "cantidad": p["cantidad"],
                "precio": p["costo"],
                "total": p["subtotal"],
            }
        )

    crear_documento("FACTURA DE COMPRA", numero, proveedor, items, archivo)

    if os.path.exists(archivo):
        os.startfile(archivo)


def factura_compra_en(id_compra):

    numero = id_compra
    archivo = f"documentos/inventario/entradas/entrada_{numero:05d}.pdf"

    # convertir a ruta absoluta
    archivo = os.path.abspath(archivo)

    # si existe abrir
    if os.path.exists(archivo):
        os.startfile(archivo)
        return

    proveedor, carrito = obtener_compra(id_compra)

    items = []

    for p in carrito:
        items.append(
            {
                "codigo": p["codigo"],
                "producto": p["descripcion"],
                "cantidad": p["cantidad"],
                "precio": p["costo"],
                "total": p["subtotal"],
            }
        )

    crear_documento("ENTRADA_INVENTARIO", numero, proveedor, items, archivo)

    if os.path.exists(archivo):
        os.startfile(archivo)
