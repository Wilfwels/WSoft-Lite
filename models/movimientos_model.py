import sqlite3
import os
from datetime import datetime
from config import *

# ================== RUTA BD ==================

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
