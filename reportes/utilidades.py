from core import *
from config import *
import sqlite3

DB_VENTAS = os.path.join(BASE_DIR, "ventas.db")


def datos_empresa():

    conn = sqlite3.connect(DB_EMPRESA)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT nombre, direccion, telefono, rif, logo
    FROM empresa
    LIMIT 1
    """)
    row = cursor.fetchone()

    conn.close()

    return {
        "nombre": row[0],
        "direccion": row[1],
        "telefono": row[2],
        "rif": row[3],
        "logo": row[4],
    }


def siguiente_numero(tipo):

    conn = sqlite3.connect("wsoft.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS numeracion(
        tipo TEXT PRIMARY KEY,
        numero INTEGER
    )
    """)

    cursor.execute("SELECT numero FROM numeracion WHERE tipo=?", (tipo,))
    row = cursor.fetchone()

    if row:

        numero = row[0] + 1

        cursor.execute("UPDATE numeracion SET numero=? WHERE tipo=?", (numero, tipo))

    else:

        numero = 1

        cursor.execute(
            "INSERT INTO numeracion(tipo,numero) VALUES(?,?)", (tipo, numero)
        )

    conn.commit()
    conn.close()

    return numero


import sqlite3
from config import DB_VENTAS


def obtener_venta(id_venta):

    conn = sqlite3.connect(DB_VENTAS)
    cur = conn.cursor()

    # Datos venta
    cur.execute(
        """
        SELECT cliente_codigo, cliente_nombre, subtotal, impuesto, total FROM ventas WHERE id = ?
    """,
        (id_venta,),
    )

    cliente_codigo, cliente_nombre, subtotal, impuesto, total = cur.fetchone()

    cliente = {"codigo": cliente_codigo, "nombre": cliente_nombre}

    # Items
    cur.execute(
        """
        SELECT codigo, descripcion, cantidad, precio, impuesto_porcentaje, impuesto_monto, subtotal
        FROM detalle_venta
        WHERE id_venta = ?
    """,
        (id_venta,),
    )

    items = []

    for r in cur.fetchall():

        #print(r)

        items.append(
            {
                "codigo": r[0],
                "descripcion": r[1],
                "cantidad": r[2],
                "precio": r[3],
                "impuesto": r[4],         # porcentaje
                "impuesto_monto": r[5],   # monto
                "subtotal": r[6],
            }
        )

    conn.close()
    
    return cliente, items, subtotal, impuesto, total

def siguiente_consecutivo(tipo):

    conn = sqlite3.connect(DB_VENTAS)
    cur = conn.cursor()

    cur.execute("SELECT numero FROM consecutivos WHERE tipo=?", (tipo,))
    row = cur.fetchone()

    if row is None:
        numero = 1
        cur.execute(
            "INSERT INTO consecutivos (tipo, numero) VALUES (?, ?)", (tipo, numero)
        )
    else:
        numero = row[0] + 1
        cur.execute("UPDATE consecutivos SET numero=? WHERE tipo=?", (numero, tipo))

    conn.commit()
    conn.close()

    return numero


import sqlite3
import os
from config import BASE_DIR

DB_COMPRAS = os.path.join(BASE_DIR, "compras.db")


def obtener_compra(id_compra):

    conn = sqlite3.connect(DB_COMPRAS)
    cur = conn.cursor()

    cur.execute("SELECT proveedor_nombre FROM compras WHERE id=?", (id_compra,))
    proveedor = cur.fetchone()[0]

    cur.execute(
        """
        SELECT codigo, descripcion, cantidad, costo, subtotal
        FROM detalle_compra
        WHERE id_compra=?
        """,
        (id_compra,),
    )

    carrito = []

    for r in cur.fetchall():
        carrito.append(
            {
                "codigo": r[0],
                "descripcion": r[1],
                "cantidad": r[2],
                "costo": r[3],
                "subtotal": r[4],
            }
        )

    conn.close()

    return proveedor, carrito


DB_MOV = os.path.join(BASE_DIR, "movimientos.db")


def obtener_entrada(id_mov):

    conn = sqlite3.connect(DB_MOV)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT codigo, descripcion, cantidad, precio
        FROM movimientos
        WHERE id=? AND tipo='ENTRADA MANUAL'
    """,
        (id_mov,),
    )

    carrito = []

    for r in cur.fetchall():
        carrito.append(
            {
                "codigo": r[0],
                "descripcion": r[1],
                "cantidad": r[2],
                "precio": r[3],
                "subtotal": r[2] * r[3],
            }
        )

    conn.close()

    return "INVENTARIO", carrito


def obtener_salida(id_mov):

    conn = sqlite3.connect(DB_MOV)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT codigo, descripcion, cantidad, precio
        FROM movimientos
        WHERE id=? AND tipo='SALIDA MANUAL'
    """,
        (id_mov,),
    )

    carrito = []

    for r in cur.fetchall():
        carrito.append(
            {
                "codigo": r[0],
                "descripcion": r[1],
                "cantidad": r[2],
                "precio": r[3],
                "subtotal": r[2] * r[3],
            }
        )

    conn.close()

    return "INVENTARIO", carrito


def siguiente_consecutivoe(tipo):

    conn = sqlite3.connect(DB_VENTAS)
    cur = conn.cursor()

    cur.execute("SELECT numero FROM consecutivos WHERE tipo=?", (tipo,))
    row = cur.fetchone()

    if row is None:
        numero = 1
        cur.execute(
            "INSERT INTO consecutivos (tipo, numero) VALUES (?, ?)", (tipo, numero)
        )
    else:
        numero = row[0] + 1
        cur.execute("UPDATE consecutivos SET numero=? WHERE tipo=?", (numero, tipo))

    conn.commit()
    conn.close()

    return numero


def siguiente_consecutivos(tipo):

    conn = sqlite3.connect(DB_VENTAS)
    cur = conn.cursor()

    cur.execute("SELECT numero FROM consecutivos WHERE tipo=?", (tipo,))
    row = cur.fetchone()

    if row is None:
        numero = 1
        cur.execute(
            "INSERT INTO consecutivos (tipo, numero) VALUES (?, ?)", (tipo, numero)
        )
    else:
        numero = row[0] + 1
        cur.execute("UPDATE consecutivos SET numero=? WHERE tipo=?", (numero, tipo))

    conn.commit()
    conn.close()

    return numero
