import sqlite3
import os
import sys
import tkinter as tk
import shutil

def obtener_ruta_base():

    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = obtener_ruta_base()

DATA_DIR = os.path.join(BASE_DIR, "db")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
LOGOS_DIR = os.path.join(BASE_DIR, "logos")


os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(LOGOS_DIR, exist_ok=True)

VERSION = "1.6"
PRODUCTO = "WSoft Lite"

LICENCIA_FILE = os.path.join(
    CONFIG_DIR,
    "wsoft.lic"
)

SYSTEM_FILE = os.path.join(
    CONFIG_DIR,
    "system.dat"
)

# ===============================
# BACKUPS
# ===============================

BACKUP_DIR = os.path.join(
    BASE_DIR,
    "backup"
)

os.makedirs(BACKUP_DIR, exist_ok=True)



# ===============================
# BASES
# ===============================

DB_INV = os.path.join(DATA_DIR, "inventario.db")
DB_VENTAS = os.path.join(DATA_DIR, "ventas.db")
DB_MOVIMI = os.path.join(DATA_DIR, "movimientos.db")
DB_COMPRAS = os.path.join(DATA_DIR, "compras.db")
DB_VENDE = os.path.join(DATA_DIR, "vendedores.db")
DB_EMPRESA = os.path.join(DATA_DIR, "empresa.db")
DB_ENTRADAS = os.path.join(DATA_DIR, "entradas.db")
DB_SALIDAS = os.path.join(DATA_DIR, "salidas.db")
DB_CATEGORIAS = os.path.join(DATA_DIR, "categorias.db")
DB_PROV = os.path.join(DATA_DIR, "proveedores.db")
DB_USUARIOS = os.path.join(DATA_DIR, "usuarios.db")
DB_CLIENTES = os.path.join(DATA_DIR, "clientes.db")

usuario_actual = None

def es_admin():
    return usuario_actual["rol"] == "ADMIN"

def obtener_empresa():
    conn = sqlite3.connect(DB_EMPRESA)
    cur = conn.cursor()

    cur.execute("SELECT nombre, logo FROM empresa LIMIT 1")
    data = cur.fetchone()

    conn.close()

    if data:
        return data
    else:
        return ("Mi Empresa", None)
    
    
def ventana_carga(mensaje="Procesando..."):
    
  
    winn = tk.CTkToplevel()
    winn.title("Wsoft Mantenimiento")

    # tamaño
    ancho = 350
    alto = 180

    # centrar ventana
    x = (winn.winfo_screenwidth() // 2) - (ancho // 2)
    y = (winn.winfo_screenheight() // 2) - (alto // 2)

    winn.geometry(f"{ancho}x{alto}+{x}+{y}")
    winn.resizable(False, False)

    # bloquear cerrar
    winn.protocol("WM_DELETE_WINDOW", lambda: None)

    
    #Label(winn, text=mensaje, font=("Arial", 11, "bold")).pack(pady=15)

    barra = tk.Progressbar(
        winn,
        mode="indeterminate",
        length=250
   )

    barra.pack(pady=10)

    barra.start(10)

    winn.update()
    return winn, barra

########################### BASE DIR ##########################
# 🔥 RUTA BASE CORRECTA (FUNCIONA EN .EXE)

def obtener_ruta_base():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = obtener_ruta_base()

LOGOS_DIR = os.path.join(BASE_DIR, "logos")
os.makedirs(LOGOS_DIR, exist_ok=True)

CARPETA_LOGOS = os.path.join(BASE_DIR, "logos")
os.makedirs(CARPETA_LOGOS, exist_ok=True)

# 📁 CARPETA LOGOS
LOGOS_DIR = os.path.join(BASE_DIR, "logos")
os.makedirs(LOGOS_DIR, exist_ok=True)

# 🖼️ LOGO POR DEFECTO
logo_origen = os.path.join(BASE_DIR, "logo.png")

logo_destino = os.path.join(
    LOGOS_DIR,
    "logo.png"
)


# ✅ COPIAR SOLO SI NO EXISTE
if os.path.exists(logo_origen):

    if not os.path.exists(logo_destino):

        shutil.copy(
            logo_origen,
            logo_destino
        )
        

########################### DATA DIR ##########################
# 🔥 RUTA BASE CORRECTA (FUNCIONA EN .EXE)

def obtener_ruta_base():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = obtener_ruta_base()

# 📁 CARPETA DATA ÚNICA
DATA_DIR = os.path.join(BASE_DIR, "db")
os.makedirs(DATA_DIR, exist_ok=True)

LOGOS_DIR = os.path.join(DATA_DIR, "logos")
os.makedirs(LOGOS_DIR, exist_ok=True)

CARPETA_LOGOS = os.path.join(DATA_DIR, "logos")
os.makedirs(CARPETA_LOGOS, exist_ok=True)

# 📁 CARPETA LOGOS
LOGOS_DIR = os.path.join(DATA_DIR, "logos")
os.makedirs(LOGOS_DIR, exist_ok=True)

# 🖼️ LOGO POR DEFECTO
logo_origen = os.path.join(DATA_DIR, "logo.png")

logo_destino = os.path.join(
    LOGOS_DIR,
    "logo.png"
)


# ✅ COPIAR SOLO SI NO EXISTE
if os.path.exists(logo_origen):

    if not os.path.exists(logo_destino):

        shutil.copy(
            logo_origen,
            logo_destino
        )
        