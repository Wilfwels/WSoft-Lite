import sqlite3
import os
from config import *
from demo_control import validar_limite_clientes

def conectar():
    return sqlite3.connect(DB_CLIENTES)


def crear_tabla_clientes():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes(
            codigo TEXT PRIMARY KEY,
            nombre TEXT,
            contacto TEXT,
            telefono TEXT,
            correo TEXT,
            direccion TEXT,
            ciudad TEXT
        )
    """)
    conn.commit()
    conn.close()


def listar_clientes(filtro=""):
    conn = conectar()
    cur = conn.cursor()
    if filtro:
        cur.execute("""
            SELECT codigo, nombre, telefono, ciudad
            FROM clientes
            WHERE codigo LIKE ? OR nombre LIKE ?
        """, (f"%{filtro}%", f"%{filtro}%"))
    else:
        cur.execute("SELECT codigo, nombre, telefono, ciudad FROM clientes")
    datos = cur.fetchall()
    conn.close()
    return datos


def obtener_cliente(codigo):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes WHERE codigo=?", (codigo,))
    data = cur.fetchone()
    conn.close()
    return data

def agregar_cliente(datos):

    # 🔒 CONTROL DEMO
    if not validar_limite_clientes():
        return False

    conn = conectar()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO clientes VALUES (?,?,?,?,?,?,?)",
        tuple(datos.values())
    )

    conn.commit()
    conn.close()

    return True

def actualizar_cliente(datos):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE clientes SET
        nombre=?, contacto=?, telefono=?, correo=?, direccion=?, ciudad=?
        WHERE codigo=?
    """, (
        datos["nombre"], datos["contacto"], datos["telefono"],
        datos["correo"], datos["direccion"], datos["ciudad"],
        datos["codigo"]
    ))
    conn.commit()
    conn.close()


def eliminar_cliente(codigo):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE codigo=?", (codigo,))
    conn.commit()
    conn.close()
