import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_SISTEMA = os.path.join(BASE_DIR, "empresa.db")


def crear_tabla_empresa():
    conn = sqlite3.connect(DB_SISTEMA)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS empresa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            rif TEXT,
            direccion TEXT,
            telefono TEXT,
            correo TEXT,
            logo TEXT,
            mensaje_ticket TEXT,
            impuesto_defecto REAL DEFAULT 0
        )
    """
    )

    conn.commit()
    conn.close()
