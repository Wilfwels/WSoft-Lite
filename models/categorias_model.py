import sqlite3
import os
from config import *
from core import *

def conectar():
    return sqlite3.connect(DB_CATEGORIAS)

def crear_tabla_categorias():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categorias(
            codigo INTEGER PRIMARY KEY,
            nombre TEXT
        )
    """)
    conn.commit()
    conn.close()


def listar_categorias(filtro=""):
    conn = conectar()
    cur = conn.cursor()
    if filtro:
        cur.execute("""
            SELECT codigo, nombre
            FROM categorias
            WHERE codigo LIKE ? OR nombre LIKE ?
            ORDER BY nombre
        """, (f"%{filtro}%", f"%{filtro}%"))
    else:
        cur.execute("SELECT codigo, nombre FROM categorias ORDER BY nombre")
    data = cur.fetchall()
    conn.close()
    return data


def obtener_categoria(codigo):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM categorias WHERE codigo=?", (codigo,))
    data = cur.fetchone()
    conn.close()
    return data

def agregar_categoria(data):
    
    conn = conectar()
    cur = conn.cursor()

    # ✅ VALIDAR CÓDIGO
    cur.execute(
        "SELECT codigo FROM categorias WHERE codigo=?",
        (data[0],)
    )

    existe = cur.fetchone()

    if existe:
        messagebox.showwarning(
            "Código duplicado",
            "Ya existe una categoria con ese código"
        )

        conn.commit()
        conn.close()

        return False

    # ✅ INSERTAR
    cur.execute(
        """
        INSERT INTO categorias (
            codigo, nombre) VALUES (?,?)
        """,
        data,
    )

    conn.commit()
    conn.close()

def actualizar_categoria(data):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE categorias SET nombre=?
        WHERE codigo=?
    """, data)
    conn.commit()
    conn.close()


def eliminar_categoria(codigo):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM categorias WHERE codigo=?", (codigo,))
    conn.commit()
    conn.close()
