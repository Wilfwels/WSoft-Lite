import sqlite3
from config import *

DB_EMPRESA = os.path.join(DATA_DIR, "empresa.db")

def obtener_config():

    conn = sqlite3.connect(DB_EMPRESA)
    cursor = conn.cursor()

    cursor.execute("SELECT nombre FROM empresa LIMIT 1")
    fila = cursor.fetchone()

    conn.close()

    if fila:
        return {"empresa": fila[0], "sistema": "WSoft"}

    return {"empresa": "EMPRESA", "sistema": "WSoft"}
