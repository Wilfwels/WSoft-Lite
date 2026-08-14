import sqlite3
from hashlib import sha256
from config import *
from config import DB_CATEGORIAS, DB_CLIENTES, DB_COMPRAS, DB_EMPRESA, DB_ENTRADAS, DB_MOVIMI, DB_PROV, DB_INV, DB_SALIDAS, DB_USUARIOS, DB_VENDE, DB_VENTAS

def hash_password(p):
    return sha256(p.encode()).hexdigest()

def crear_bd_si_no_existe():

    # ================= USUARIOS =================
    conn = sqlite3.connect(DB_USUARIOS)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        clave TEXT,
        rol TEXT,
        estado INTEGER DEFAULT 1
    )
    """)

    # 🔥 asegurar admin SIEMPRE
    cur.execute("SELECT 1 FROM usuarios WHERE usuario = ?", ("wels",))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO usuarios (usuario, clave, rol, estado) VALUES (?, ?, 'ADMIN', 1)",
            ("admin", hash_password("1234")),
        )

    conn.commit()
    conn.close()

   
    # ================= CLIENTES =================
    conn = sqlite3.connect(DB_CLIENTES)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clientes (codigo TEXT PRIMARY KEY, nombre TEXT, contacto TEXT, telefono TEXT, correo TEXT, direccion TEXT, ciudad TEXT)""")
    cur.execute("INSERT INTO clientes (codigo, nombre, contacto, telefono, correo, direccion, ciudad) VALUES ('C01', 'CONTADO', ' ', ' ', ' ', ' ', ' ')",)
    conn.commit()
    conn.close()

    # ================= CATEGORIAS =================
    conn = sqlite3.connect(DB_CATEGORIAS)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS categorias (codigo TEXT PRIMARY KEY, nombre TEXT UNIQUE)""")
    cur.execute("INSERT INTO categorias (codigo, nombre) VALUES ('01', 'VARIOS')",)
    conn.commit()
    conn.close()

    # ================= PROVEEDORES =================
    conn = sqlite3.connect(DB_PROV)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS proveedores (codigo TEXT PRIMARY KEY, nombre TEXT, contacto TEXT, telefono TEXT, registro TEXT, direccion TEXT,ciudad TEXT)""")
    cur.execute("INSERT INTO proveedores (codigo, nombre, contacto, telefono, registro, direccion, ciudad) VALUES ('01', 'PROVEEDOR GENERAL', 'WSOFT SQLITE', ' ', ' ', ' ', ' ')",)
    conn.commit()
    conn.close()


    # ================= INVENTARIO =================
    conn = sqlite3.connect(DB_INV)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventario (
        codigo TEXT PRIMARY KEY,
        proveedor INTEGER,
        descripcion TEXT,
        cantidad REAL,
        costo REAL,
        porcentaje INTEGER,
        impuesto REAL,
        precio_detal REAL,
        precio_mayor REAL,
        categoria INTEGER,
        fecha_compra TEXT,
        stock_minimo INTEGER
    )
    """)                
    conn.commit()
    conn.close()

    # ================= COMPRAS =================
    conn = sqlite3.connect(DB_COMPRAS)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        proveedor_codigo TEXT,
        proveedor_nombre TEXT,
        subtotal REAL,
        impuesto REAL,
        total REAL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS detalle_compra (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_compra INTEGER,
        codigo TEXT,
        descripcion TEXT,
        cantidad REAL,
        costo REAL,
        subtotal REAL
    )
    """)
    conn.commit()
    conn.close()

    # ================= ENTRADAS =================
    conn = sqlite3.connect(DB_ENTRADAS)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        proveedor_codigo TEXT,
        proveedor_nombre TEXT,
        subtotal REAL,
        impuesto REAL,
        total REAL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS detalle_compra (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_compra INTEGER,
        codigo TEXT,
        descripcion TEXT,
        cantidad REAL,
        costo REAL,
        subtotal REAL
    )
    """)
    conn.commit()
    conn.close()

    # ================= VENTAS =================
    conn = sqlite3.connect(DB_VENTAS)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        tipo_pago TEXT,
        tipo_precio TEXT,
        cliente_codigo TEXT,
        cliente_nombre TEXT,
        vendedor_codigo TEXT,
        subtotal REAL,
        impuesto REAL,
        total REAL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS detalle_venta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_venta INTEGER,
        codigo TEXT,
        descripcion TEXT,
        cantidad REAL,
        precio REAL,
        subtotal REAL,
        impuesto_porcentaje REAL,
        impuesto_monto REAL
    )
    """)
    conn.commit()
    conn.close()

    # ================= SALIDAS =================
    conn = sqlite3.connect(DB_SALIDAS)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        cliente_codigo TEXT,
        cliente_nombre TEXT,
        subtotal REAL,
        impuesto REAL,
        total REAL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS detalle_venta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_venta INTEGER,
        codigo TEXT,
        descripcion TEXT,
        cantidad REAL,
        precio REAL,
        subtotal REAL
    )
    """)
    conn.commit()
    conn.close()

    # ================= MOVIMIENTOS =================
    conn = sqlite3.connect(DB_MOVIMI)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS movimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        producto_id TEXT,
        tipo TEXT,
        cantidad REAL,
        referencia TEXT
    )
    """)
    conn.commit()
    conn.close()


    # ================= VENDEDORES =================
    conn = sqlite3.connect(DB_VENDE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vendedores (codigo TEXT PRIMARY KEY, nombre TEXT, contacto TEXT, telefono TEXT, correo TEXT, direccion TEXT, ciudad TEXT)""")
    cur.execute("INSERT INTO vendedores (codigo, nombre, contacto, telefono, correo, direccion, ciudad) VALUES ('01', 'VENDEDOR ESTRELLA', ' ', ' ', ' ', ' ', ' ')",)
    conn.commit()
    conn.close()

# ================= EMPRESA =================

conn = sqlite3.connect(DB_EMPRESA)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS empresa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    rif TEXT,
    direccion TEXT,
    telefono TEXT,
    correo TEXT,
    logo TEXT,
    mensaje_ticket TEXT,
    impuesto_defecto REAL,
    impresion_venta TEXT,
    abrir_pdf_venta
)
""")


# 🔥 INSERT DEMO SOLO SI NO HAY DATOS

cur.execute("SELECT COUNT(*) FROM empresa")


if cur.fetchone()[0] == 0:

    # =========================================
    # COPIAR LOGO INICIAL DE WSOFT
    # =========================================

    import shutil

    origen_logo = os.path.join(
        BASE_DIR,
        "_internal",
        "logos",
        "wsoft.png"
    )

    destino_logo = os.path.join(
        LOGOS_DIR,
        "wsoft.png"
    )


    os.makedirs(
        LOGOS_DIR,
        exist_ok=True
    )


    if os.path.exists(origen_logo):

        if not os.path.exists(destino_logo):

            shutil.copy(
                origen_logo,
                destino_logo
            )


    # Nombre que se guarda en la BD
    logo_demo = "wsoft.png"


    cur.execute(
        """
        INSERT INTO empresa
        (nombre, rif, direccion, telefono, correo, logo, mensaje_ticket, impuesto_defecto, impresion_venta, abrir_pdf_venta)
        VALUES (?,?,?,?,?,?,?,?,?,?)
        """,
        (
            "EMPRESA DEMO WSOFT",
            "J-00000000-0",
            "Dirección Demo",
            "0000-0000000",
            "demo@wsoft.com",
            logo_demo,
            "Gracias por su compra",
            0.0,
            "TICKET",
            0
        ),
    )


conn.commit()
conn.close()