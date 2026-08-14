import sqlite3
import os
from datetime import datetime
from config import *
from core import *
from demo_control import validar_limite_productos

# ================== CONEXIÓN ==================
def conectar(db=DB_INV):
    return sqlite3.connect(db)


# ================== TABLA ==================
def crear_tabla_inventario():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventario(
            codigo INTEGER PRIMARY KEY,
            proveedor INTEGER,
            descripcion TEXT,
            cantidad INTEGER,
            costo REAL,
            porcentaje INTEGER,
            impuesto REAL,
            precio_detal REAL,
            precio_mayor REAL,
            categoria INTEGER,
            fecha_compra TEXT,
            stock_minimo INTEGER
        )
    """)
    conn.commit()
    conn.close()


# ================== LISTAR ==================
def listar_inventario(filtro=""):
    conn = conectar()
    cur = conn.cursor()

    if filtro:
        cur.execute(
            """
            SELECT * FROM inventario
            WHERE codigo LIKE ? OR descripcion LIKE ?
            ORDER BY descripcion
        """,
            (f"%{filtro}%", f"%{filtro}%"),
        )
    else:
        cur.execute("SELECT * FROM inventario ORDER BY descripcion")

    filas = cur.fetchall()
    conn.close()
    return filas

def agregar_producto(data):

    if not validar_limite_productos():
        return False

    conn = conectar()
    cur = conn.cursor()

    # ✅ VALIDAR CÓDIGO
    cur.execute(
        "SELECT codigo FROM inventario WHERE codigo=?",
        (data[0],)
    )

    existe = cur.fetchone()

    if existe:
        messagebox.showwarning(
            "Código duplicado",
            "Ya existe un producto con ese código"
        )

        conn.commit()
        conn.close()

        return False

    # ✅ INSERTAR
    cur.execute(
        """
        INSERT INTO inventario (
            codigo, proveedor, descripcion, cantidad, costo,
            porcentaje, impuesto, precio_detal, precio_mayor,
            categoria, fecha_compra, stock_minimo
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        data,
    )

    conn.commit()
    conn.close()

    return True

# ================== ACTUALIZAR ==================
def actualizar_producto(data):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE inventario SET
            proveedor=?,
            descripcion=?,
            cantidad=?,
            costo=?,
            porcentaje=?,
            impuesto=?,
            precio_detal=?,
            precio_mayor=?,
            categoria=?,
            fecha_compra=?,
            stock_minimo=?
        WHERE codigo=?
    """,
    data,
    )
    conn.commit()
    conn.close()


# ================== ELIMINAR ==================
def eliminar_producto(codigo):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM inventario WHERE codigo = ?", (codigo,))
    conn.commit()
    conn.close()


# ================== PROVEEDORES ==================
def cargar_proveedores():
    conn = conectar(DB_PROV)
    cur = conn.cursor()
    cur.execute("SELECT codigo, nombre FROM proveedores ORDER BY nombre")
    datos = cur.fetchall()
    conn.close()
    return datos


# ================== CATEGORÍAS ==================
def cargar_categorias():
    conn = conectar(DB_CATEGORIAS)
    cur = conn.cursor()
    cur.execute("SELECT codigo, nombre FROM categorias ORDER BY nombre")
    datos = cur.fetchall()
    conn.close()
    return datos


# ======================================================0
def buscar_producto_db(texto):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT codigo, descripcion, cantidad, costo, impuesto
        FROM inventario
        WHERE codigo LIKE ? OR descripcion LIKE ?
        ORDER BY descripcion
        """,
        (f"%{texto}%", f"%{texto}%"),
    )
    datos = cur.fetchall()
    conn.close()
    return datos


def obtener_faltantes():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT codigo, descripcion, cantidad, stock_minimo
        FROM inventario
        WHERE cantidad <= stock_minimo
        ORDER BY cantidad ASC
    """)

    datos = cur.fetchall()
    conn.close()

    return datos
