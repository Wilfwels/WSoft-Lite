import sqlite3
import os

from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_MOVIMI = os.path.join(BASE_DIR, "movimientos.db")


def registrar_movimiento(producto_id, tipo, cantidad, referencia):
    conn = sqlite3.connect(DB_MOVIMI)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO movimientos
        (producto_id, tipo, cantidad, fecha, referencia)
        VALUES (?, ?, ?, ?, ?)
    """,
        (
            producto_id,
            tipo,
            cantidad,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            referencia,
        ),
    )

    conn.commit()
    conn.close()
