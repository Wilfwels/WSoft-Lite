import sqlite3
from tkinter import messagebox

from licencias import verificar_licencia

from config import (
    DB_INV,
    DB_CLIENTES,
    DB_PROV
)


# ===============================
# LIMITES DEMO
# ===============================

LIMITES = {
    "productos": 5,
    "clientes": 5,
    "proveedores": 5,
}


# ===============================
# LICENCIA
# ===============================

def obtener_licencia():
    return verificar_licencia()


def es_demo():

    licencia = obtener_licencia()

    return licencia.get("plan") == "DEMO"


# ===============================
# CONTADORES
# ===============================

def contar_productos():

    conn = sqlite3.connect(DB_INV)
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM inventario"
    )

    cantidad = cur.fetchone()[0]

    conn.close()

    return cantidad


def contar_clientes():

    conn = sqlite3.connect(DB_CLIENTES)
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM clientes"
    )

    cantidad = cur.fetchone()[0]

    conn.close()

    return cantidad


def contar_proveedores():

    conn = sqlite3.connect(DB_PROV)
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM proveedores"
    )

    cantidad = cur.fetchone()[0]

    conn.close()

    return cantidad


# ===============================
# VALIDACIONES
# ===============================

def validar_limite_productos():

    if not es_demo():
        return True

    cantidad = contar_productos()

    limite = LIMITES["productos"]

    if cantidad >= limite:

        messagebox.showwarning(
            "Versión DEMO",
            f"La versión DEMO permite registrar "
            f"un máximo de {limite} productos."
        )

        return False

    return True


def validar_limite_clientes():

    if not es_demo():
        return True

    cantidad = contar_clientes()

    limite = LIMITES["clientes"]

    if cantidad >= limite:

        messagebox.showwarning(
            "Versión DEMO",
            f"La versión DEMO permite registrar "
            f"un máximo de {limite} clientes."
        )

        return False

    return True


def validar_limite_proveedores():

    if not es_demo():
        return True

    cantidad = contar_proveedores()

    limite = LIMITES["proveedores"]

    if cantidad >= limite:

        messagebox.showwarning(
            "Versión DEMO",
            f"La versión DEMO permite registrar "
            f"un máximo de {limite} proveedores."
        )

        return False

    return True