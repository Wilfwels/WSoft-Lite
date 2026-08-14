import sqlite3
import os
from config import *
from core import *

def conectar():
    return sqlite3.connect(DB_VENDE)

def crear_tabla_vendedores():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendedores(
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


def listar_vendedores(filtro=""):
    conn = conectar()
    cur = conn.cursor()
    if filtro:
        f = f"%{filtro.upper()}%"
        cur.execute(
            "SELECT * FROM vendedores WHERE codigo LIKE ? OR nombre LIKE ?",
            (f, f)
        )
    else:
        cur.execute("SELECT * FROM vendedores")
    filas = cur.fetchall()
    conn.close()
    return filas

def obtener_vendedor(codigo):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM vendedores WHERE codigo=?", (codigo,))
    data = cur.fetchone()
    conn.close()
    return data


def agregar_vendedor(data):
    
    conn = conectar()
    cur = conn.cursor()

    # ✅ VALIDAR CÓDIGO
    cur.execute(
        "SELECT codigo FROM vendedores WHERE codigo=?",
        (data[0],)
    )

    existe = cur.fetchone()

    if existe:
        messagebox.showwarning(
            "Código duplicado",
            "Ya existe un vendedor con ese código"
        )

        conn.commit()
        conn.close()

        return False

    # ✅ INSERTAR
    cur.execute(
        """
        INSERT INTO vendedores (codigo, nombre, contacto, telefono, correo, direccion, ciudad) VALUES (?,?,?,?,?,?,?)
        """,
        data,
    )
    conn.commit()
    conn.close()

def actualizar_vendedor(data):
    conn = conectar()
    cur = conn.cursor()  
    cur.execute("""
        UPDATE vendedores SET 
            nombre=?, contacto=?, telefono=?, 
            correo=?, direccion=?, ciudad=?
        WHERE codigo=?
    """, data)
    conn.commit()
    conn.close()

def eliminar_vendedor(codigo):
    conn = conectar()
    cur = conn.cursor()
    print("✅ pasa por eliminar")
    cur.execute("DELETE FROM vendedores WHERE codigo=?", (codigo,))
    conn.commit()
    conn.close()
