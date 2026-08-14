from reportes.plantilla import crear_documento
from reportes.utilidades import siguiente_numero


def factura_salida(cliente, carrito):

    numero = siguiente_numero("SALIDA")

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

    crear_documento("DOCUMENTO SALIDA", numero, cliente, items, archivo)


import os
from reportes.utilidades import obtener_salida


def salida_inventario_id(id_mov):

    numero = id_mov

    archivo = f"documentos/salidas/salida_{numero:05d}.pdf"

    if os.path.exists(archivo):
        os.startfile(archivo)
        return

    cliente, carrito = obtener_salida(id_mov)

    items = []

    for p in carrito:
        items.append(
            {
                "codigo": p["codigo"],
                "producto": p["descripcion"],
                "cantidad": p["cantidad"],
                "precio": p["precio"],
                "total": p["subtotal"],
            }
        )

    crear_documento("DOCUMENTO SALIDA", numero, cliente, items, archivo)

    os.startfile(archivo)
