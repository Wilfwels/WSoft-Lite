import sqlite3
import os
from config import *
from core import *
from demo_control import validar_limite_proveedores

def conectar():
    return sqlite3.connect(DB_PROV)


def crear_tabla_proveedores():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS proveedores(
            codigo TEXT PRIMARY KEY,
            nombre TEXT,
            contacto TEXT,
            telefono TEXT,
            registro TEXT,
            direccion TEXT,
            ciudad TEXT
        )
    """)
    conn.commit()
    conn.close()


def listar_proveedores(filtro=""):
    conn = conectar()
    cur = conn.cursor()
    if filtro:
        cur.execute("""
            SELECT codigo, nombre, telefono, ciudad
            FROM proveedores
            WHERE codigo LIKE ? OR nombre LIKE ?
            ORDER BY nombre
        """, (f"%{filtro}%", f"%{filtro}%"))
    else:
        cur.execute("""
            SELECT codigo, nombre, telefono, ciudad
            FROM proveedores
            ORDER BY nombre
        """)
    datos = cur.fetchall()
    conn.close()
    return datos


def obtener_proveedor(codigo):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM proveedores WHERE codigo=?", (codigo,))
    dato = cur.fetchone()
    conn.close()
    return dato

def agregar_proveedor(data):

    # 🔒 VALIDAR LIMITE DEMO
    if not validar_limite_proveedores():
        return False

    conn = conectar()
    cur = conn.cursor()

    # ✅ VALIDAR CÓDIGO
    cur.execute(
        "SELECT codigo FROM proveedores WHERE codigo=?",
        (data[0],)
    )

    existe = cur.fetchone()

    if existe:
        messagebox.showwarning(
            "Código duplicado",
            "Ya existe un proveedor con ese código"
        )

        conn.close()

        return False

    # ✅ INSERTAR

    cur.execute(
        """
        INSERT INTO proveedores (
            codigo,
            nombre,
            contacto,
            telefono,
            registro,
            direccion,
            ciudad
        )
        VALUES (?,?,?,?,?,?,?)
        """,
        data,
    )

    conn.commit()
    conn.close()

    return True


def actualizar_proveedor(data):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE proveedores SET
            nombre=?, contacto=?, telefono=?,
            registro=?, direccion=?, ciudad=?
        WHERE codigo=?
    """, data)
    conn.commit()
    conn.close()


def eliminar_proveedor(codigo):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM proveedores WHERE codigo=?", (codigo,))
    conn.commit()
    conn.close()
