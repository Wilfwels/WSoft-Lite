from reportes.plantilla import crear_documento
from reportes.utilidades import siguiente_numero, obtener_venta
import os

def factura_venta(id_venta):

    numero = id_venta
    archivo = f"documentos/facturas_venta/factura_{numero:05d}.pdf"

    # print("BUSCANDO:", archivo)
    # print("EXISTE:", os.path.exists(archivo))

    archivo = os.path.abspath(archivo)  # 👈 clave

    if os.path.exists(archivo):
        return archivo

    # obtener datos
    cliente, carrito, subtotal, impuesto, total = obtener_venta(id_venta)


    items = []

    for p in carrito:

        items.append(
            {
                "codigo": p["codigo"],
                "descripcion": p["descripcion"],
                "cantidad": p["cantidad"],
                "precio": p["precio"],
                "impuesto": p.get("impuesto", 0),
                "impuesto_monto": p.get("impuesto_monto", 0),
                "subtotal": p["subtotal"],
            }
        )
        
    crear_documento("FACTURA DE VENTA", numero, cliente, items, archivo, subtotal, impuesto, total)
    #print("RUTA FACTURA:", archivo)
    return archivo   


def factura_salidas(id_venta):

    numero = id_venta
    archivo = f"documentos/inventario/salidas/salida_{numero:05d}.pdf"

    # print("BUSCANDO:", archivo)
    # print("EXISTE:", os.path.exists(archivo))

    archivo = os.path.abspath(archivo)  # 👈 clave

    if os.path.exists(archivo):
        return archivo

    # obtener datos
    cliente, carrito = obtener_venta(id_venta)

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

    # crear pdf
    crear_documento("SALIDA DE INVENTARIO", numero, cliente, items, archivo)
    return archivo