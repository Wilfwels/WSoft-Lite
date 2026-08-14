import inventario
import proveedores
import categorias
import vendedores
import clientes
import ventas
import compras
import kardex
import kardex_general
import kardex_total
import inventario_valorizado
import config
import os
import usuarios_admin
from licencias import verificar_licencia
from core import *
from config import *
from config import obtener_empresa
from reportes.reporte_faltantes import abrir_reporte_faltantes
from movimientos import abrir_movimientos
from reportes.reporte_vendedores import abrir_reporte_vendedores
from reportes.reporte_totales_vendedores import abrir_reporte_totales_vendedores
from crearbases import crear_bd_si_no_existe
from backup import crear_backup
from backup import restaurar_backup

def obtener_datos_licencia():

    return verificar_licencia()

ESTADO_LICENCIA = verificar_licencia()


if (
    ESTADO_LICENCIA["estado"] == "BLOQUEADA"
    or ESTADO_LICENCIA["estado"] == "VENCIDA"
    or (
        ESTADO_LICENCIA["estado"] == "DEMO"
        and ESTADO_LICENCIA.get("dias", 0) <= 0
    )
):

    messagebox.showerror(
        "WSoft Lite",
        ESTADO_LICENCIA.get(
            "mensaje",
            "Licencia expirada"
        )
    )

    exit()

def ejecutar_backup():

    carpeta = filedialog.askdirectory(
        title="Seleccione donde guardar el respaldo"
    )

    if not carpeta:
        return


    ok, ruta = crear_backup(carpeta)


    if ok:

        messagebox.showinfo(
            "Backup",
            f"Respaldo creado correctamente:\n\n{ruta}"
        )
        
def ejecutar_restaurar():

    ruta = filedialog.askdirectory(
        title="Seleccionar carpeta de backup"
    )

    if not ruta:
        return


    respuesta = messagebox.askyesno(
        "Restaurar Backup",
        "⚠️ Esta acción reemplazará los datos actuales.\n\n¿Desea continuar?"
    )

    if not respuesta:
        return


    try:

        ok, msg = restaurar_backup(ruta)


        if ok:

            messagebox.showinfo(
                "Restauración",
                "✅ Restauración completada correctamente.\n\nReinicie WSoft Lite para aplicar los cambios."
            )

        else:

            messagebox.showwarning(
                "Restauración",
                msg
            )


    except Exception as e:

        messagebox.showerror(
            "Error Restaurando",
            str(e)
        )
        
        
carpetas = [
    "documentos",
    "documentos/facturas_venta",
    "documentos/facturas_compra",
    "documentos/tickets",
    "documentos/inventario",
    "documentos/inventario/entradas",
    "documentos/inventario/salidas",
]

for carpeta in carpetas:
    os.makedirs(carpeta, exist_ok=True)
    
def sistema_inicializado():
    return os.path.exists(DB_USUARIOS)


if not sistema_inicializado():
    print("⚠ Inicializando sistema...")
    crear_bd_si_no_existe()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


menu = None  # menú global
refrescar_dashboard = None

# ........................DASHBOARD....................

def obtener_dashboard_completo():

    # ==============================
    # DATOS INVENTARIO
    # ==============================

    total_productos, stock_bajo, sin_stock, valor = obtener_datos_dashboard()


    # ==============================
    # DATOS LICENCIA
    # ==============================

    licencia = verificar_licencia()


    return {

        "productos": total_productos,

        "stock_bajo": stock_bajo,

        "sin_stock": sin_stock,

        "valor": valor,

        "licencia": licencia

    }
    
def obtener_datos_dashboard():

    nombre_empresa, ruta_logo = obtener_empresa()
    conn = sqlite3.connect(DB_INV)
    cur = conn.cursor()

    # total productos
    cur.execute("SELECT COUNT(*) FROM inventario")
    total_productos = cur.fetchone()[0]

    # sin stock
    cur.execute("SELECT COUNT(*) FROM inventario WHERE cantidad <= 0")
    sin_stock = cur.fetchone()[0]

    # stock bajo
    cur.execute("SELECT COUNT(*) FROM inventario WHERE cantidad > 0 AND cantidad <= 5")
    stock_bajo = cur.fetchone()[0]

    # valor total inventario
    cur.execute("SELECT SUM(cantidad * costo) FROM inventario")
    valor = cur.fetchone()[0]

    conn.close()

    if valor is None:
        valor = 0

    return total_productos, stock_bajo, sin_stock, valor

def obtener_ventas_hoy():

    conn = sqlite3.connect(DB_VENTAS)
    cur = conn.cursor()

    try:

        cur.execute("""
        SELECT SUM(total)
        FROM ventas
        WHERE substr(fecha,1,10) = date('now')
        """)

        valor = cur.fetchone()[0]

        if valor is None:
            valor = 0

    except:
        valor = 0

    conn.close()

    return valor


def obtener_ventas_mes():

    conn = sqlite3.connect(DB_INV)
    cur = conn.cursor()

    try:

        cur.execute("""
        SELECT strftime('%d', fecha), SUM(total)
        FROM ventas
        GROUP BY strftime('%d', fecha)
        """)

        datos = cur.fetchall()

    except:
        datos = []

    conn.close()

    dias = []
    totales = []

    for d in datos:
        dias.append(d[0])
        totales.append(d[1])

    return dias, totales


def obtener_top_productos():

    conn = sqlite3.connect(DB_INV)
    cur = conn.cursor()

    try:

        cur.execute("""
        SELECT descripcion, SUM(cantidad)
        FROM ventas_detalle
        GROUP BY descripcion
        ORDER BY SUM(cantidad) DESC
        LIMIT 5
        """)

        datos = cur.fetchall()

    except:
        datos = []

    conn.close()

    return datos


# ===================== UTILIDADES =====================


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def conectar_db():
    conn = sqlite3.connect(DB_USUARIOS)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        clave TEXT,
        rol TEXT DEFAULT 'VENDEDOR',
        estado INTEGER DEFAULT 1
    )
    """)

    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN rol TEXT DEFAULT 'VENDEDOR'")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN estado INTEGER DEFAULT 1")
    except:
        pass

    conn.commit()

    return conn  # 🔥 IMPORTANTE


# ===================== ABRIR MÓDULOS =====================
def abrir_inventario():
    inventario.abrir_inventario(menu)


def abrir_proveedores():
    proveedores.abrir_proveedores(menu)


def abrir_categoria():
        
    categorias.abrir_categorias(menu)


def abrir_vendedores():
    vendedores.abrir_vendedores(menu)


def abrir_clientes():
    clientes.abrir_clientes(menu)

def abrir_ventas():
    ventas.abrir_ventas(menu, refrescar_dashboard)

def abrir_compras(modo="COMPRA"):
    compras.abrir_compras(menu, modo, refrescar_dashboard)



# ===================== LOGIN =====================
def validar_login():
    
    user = entry_usuario.get().strip()
    pwd = hash_password(entry_clave.get())

    if not user or not pwd:
        messagebox.showerror("Error", "Complete todos los campos")
        return

    conn = sqlite3.connect(DB_USUARIOS)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT usuario, rol 
        FROM usuarios 
        WHERE usuario=? AND clave=? AND estado=1
        """,
        (user, pwd),
    )

    data = cursor.fetchone()
    conn.close()

    if data:

        config.usuario_actual = {"usuario": data[0], "rol": data[1]}

        app.withdraw()
        abrir_menu(config.usuario_actual)

    else:
        messagebox.showerror("Error", "Credenciales incorrectas")


def mostrar_clave():
    entry_clave.config(show="" if entry_clave.cget("show") == "*" else "*")


# ===================== MENÚ =====================
def abrir_menu(usuario):

    global menu
    global refrescar_dashboard
    menu = tk.Toplevel(app)
    
    menu.title(f"{PRODUCTO} {VERSION} - Sistema de Gestión Comercial")
    menu.state("zoomed")
    menu.configure(bg="#2c2c44")
    menu.focus_force()
    

    def salir_completo():
        app.destroy()

    menu.protocol("WM_DELETE_WINDOW", salir_completo)

    sidebar = tk.Frame(menu, bg="#111122", width=260)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)
    # ===== PANEL DERECHO =====
    panel = tk.Frame(menu, bg="#1e1e2f")
    panel.pack(side="right", fill="both", expand=True)

    # ===== BARRA SUPERIOR =====
    barra_superior = tk.Frame(panel, bg="#2c2c44", height=60)
    barra_superior.pack(fill="x")

    plan = ESTADO_LICENCIA.get(
        "plan",
        ESTADO_LICENCIA["estado"]
    )

    label_usuario = tk.Label(
        barra_superior,
        text=(
            f"👤 Usuario: {usuario['usuario']} "
            f"({usuario['rol']})   |   "
            f"Licencia: {ESTADO_LICENCIA['plan']} "
            f"|   Días: {ESTADO_LICENCIA.get('dias',0)}"
        ),
        bg="#2c2c44",
        fg="white", 
        font=("Segoe UI", 12, "bold"),
    )
    
    label_usuario.pack(side="left", padx=20)
    
    # Fecha y hora
    label_fecha = tk.Label(
        barra_superior,
        bg="#2c2c44",
        fg="white",
        font=("Segoe UI", 12),
    )
    label_fecha.pack(side="right", padx=20)

    def btn(texto, comando, parent):
        b = tk.Button(
            parent,
            text=texto,
            font=("Segoe UI", 11),
            bg="#1e1e2f",
            fg="white",
            relief="flat",
            width=22,
            height=1,  # antes era 2
            anchor="w",
            padx=15,
            pady=4,  # más compacto
            command=comando,
        )
        b.pack(fill="x", pady=1)
        return b

    after_id = None

    def actualizar_hora():
        global after_id

        ahora = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
        label_fecha.config(text=f"🕓  {ahora}")

        # 🔥 GUARDAR EL ID
        after_id = menu.after(1000, actualizar_hora)   
        
        
    def al_cerrar():
        global after_id

        if after_id:
            try:
                menu.after_cancel(after_id)
            except:
                pass

        app.destroy()

    actualizar_hora()
    app.protocol("WM_DELETE_WINDOW", al_cerrar)
    
    # ===== CONTENIDO DASHBOARD =====

    nombre_empresa, ruta_logo = obtener_empresa()

    contenido = tk.Frame(panel, bg="#1e1e2f")
    contenido.pack(fill="both", expand=True, padx=30, pady=40)

    try:

        if ruta_logo:

            ruta_logo = os.path.join(
                LOGOS_DIR,
                ruta_logo
            )

            if os.path.exists(ruta_logo):

                img = Image.open(ruta_logo)
                img = img.resize((200, 200))

                logo = ImageTk.PhotoImage(img)

                lbl_logo = tk.Label(
                    contenido,
                    image=logo,
                    bg="#1e1e2f"
                )

                lbl_logo.image = logo
                lbl_logo.pack(pady=10)

    except Exception as e:
        print("Error cargando logo dashboard:", e)


    tk.Label(
        contenido,
        text=nombre_empresa,
        bg="#1e1e2f",
        fg="#f7f8fa",
        font=("Segoe UI", 28, "bold"),
    ).pack()
    
    tk.Label(
        contenido,
        text="Sistema de Gestión Comercial 🔵 Inventario 🔵 Ventas  🔵 Compras",
        bg="#1e1e2f",
        fg="#f7f8fa",
        font=("Segoe UI", 14, "bold"),
    ).pack()

    total_productos, stock_bajo, sin_stock, valor = obtener_datos_dashboard()

    # espacio para bajar las cards
    # tk.Frame(contenido, height=80, bg="#1e1e2f").pack()

    frame_cards = tk.Frame(contenido, bg="#1e1e2f")
    frame_cards.pack(pady=10)
    
    labels_dashboard = {}

    def card(titulo, valor, color):

        f = tk.Frame(frame_cards, bg=color, width=200, height=160)
        f.pack(side="left", padx=2)
        f.pack_propagate(False)

        tk.Label(
            f,
            text=titulo,
            bg=color,
            fg="white",
            font=("Segoe UI", 12, "bold"),
        ).pack(pady=10)

        lbl_valor = tk.Label(
            f,
            text=valor,
            bg=color,
            fg="white",
            font=("Segoe UI", 18, "bold"),
        )
        lbl_valor.pack()

        labels_dashboard[titulo] = lbl_valor
        
    ventas_hoy = obtener_ventas_hoy()
    
    datos = obtener_dashboard_completo()

    licencia = datos["licencia"]


    card("📦 Productos", total_productos, "#6d99f7")
    card("⚠ Stock Bajo", stock_bajo, "#d8b181")
    card("📉 Sin Stock", sin_stock, "#c07575")
    card("💰 Valor Inventario", f"${valor:,.0f}", "#234B3D")
    card("💵 Ventas Hoy", f"${ventas_hoy:,.0f}", "#8a62cf")


    texto_licencia = (
        f"{licencia.get('estado')}\n"
        f"{licencia.get('plan')}\n"
        f"{licencia.get('dias',0)} días"
    )


    card(
        "🔐 Licencia",
        texto_licencia,
        "#f88f06"
    )
        
    def refrescar_dashboard_local():
        
        global refrescar_dashboard

        total_productos, stock_bajo, sin_stock, valor = obtener_datos_dashboard()
        ventas_hoy = obtener_ventas_hoy()

        labels_dashboard["📦 Productos"].config(text=str(total_productos))
        labels_dashboard["⚠ Stock Bajo"].config(text=str(stock_bajo))
        labels_dashboard["📉 Sin Stock"].config(text=str(sin_stock))
        labels_dashboard["💰 Valor Inventario"].config(text=f"${valor:,.0f}")
        labels_dashboard["💵 Ventas Hoy"].config(text=f"${ventas_hoy:,.0f}")
        
    refrescar_dashboard = refrescar_dashboard_local

    #print("Dashboard actualizado")

    frame_accesos = tk.Frame(contenido, bg="#1e1e2f")
    frame_accesos.pack(pady=15)

    def btn_acceso(parent, texto, comando):
        b = tk.Button(
            parent,
            text=texto,
            command=comando,
            bg="#4D576B",
            fg="white",
            font=("Segoe UI", 14, "bold"),
            width=28,
            height=4,
            relief="flat",
            cursor="hand2",
        )
        return b

    botones = [
        ("💰 VENTAS", abrir_ventas),
        ("🧾 COMPRAS", lambda: abrir_compras("COMPRA")),
        ("📦 INVENTARIO", abrir_inventario),
        ("👥 CLIENTES", abrir_clientes),
        ("🏢 PROVEEDORES", abrir_proveedores),
        ("🧑‍💼 VENDEDORES", abrir_vendedores),
    ]

    fila1 = tk.Frame(frame_accesos, bg="#1e1e2f")
    fila1.pack()

    fila2 = tk.Frame(frame_accesos, bg="#1e1e2f")
    fila2.pack()

    for i, (txt, cmd) in enumerate(botones):
        if i < 3:
            btn_acceso(fila1, txt, cmd).pack(side="left", padx=5, pady=5)
        else:
            btn_acceso(fila2, txt, cmd).pack(side="left", padx=5, pady=5)

    # ===== ACORDEÓN =====
    grupos = {}
    botones = {}

    def mostrar(nombre):
        if grupos[nombre].winfo_ismapped():
            grupos[nombre].pack_forget()
            botones[nombre].config(bg="#1e1e2f", fg="white")
            return

        for k, g in grupos.items():
            g.pack_forget()
            botones[k].config(bg="#1e1e2f", fg="white")

            for w in g.winfo_children():
                if isinstance(w, tk.Button):
                    w.config(bg="#1e1e2f", fg="white")

        grupos[nombre].pack(fill="x")
        botones[nombre].config(bg="#3b82f6", fg="white")

        for w in grupos[nombre].winfo_children():
            if isinstance(w, tk.Button):
                w.config(bg="#2563eb", fg="white")

    # ===== OPERACIONES =====
    btn_op = btn("▶ 🧾 Operaciones", lambda: mostrar("op"), sidebar)
    frame_op = tk.Frame(sidebar, bg="#111122")

    btn("   🧾 Compras", lambda: abrir_compras("COMPRA"), frame_op)
    btn("   📥 Entradas", lambda: abrir_compras("ENTRADA"), frame_op)
    btn("   📤 Salidas", lambda: abrir_compras("SALIDA"), frame_op)
    btn("   💰 Ventas", abrir_ventas, frame_op)

    grupos["op"] = frame_op
    botones["op"] = btn_op

    # ===== INVENTARIO =====
    btn_inv = btn("▶ 📦 Inventario", lambda: mostrar("inv"), sidebar)
    frame_inv = tk.Frame(sidebar, bg="#111122")
    btn("   📦 Productos", abrir_inventario, frame_inv)
    btn("   🧾 Categorías", abrir_categoria, frame_inv)

    grupos["inv"] = frame_inv
    botones["inv"] = btn_inv

    # ===== GESTIÓN =====
    btn_ges = btn("▶ 👥 Gestión", lambda: mostrar("ges"), sidebar)
    frame_ges = tk.Frame(sidebar, bg="#111122")
    btn("   🏢 Proveedores", abrir_proveedores, frame_ges)
    btn("   🧑‍💼 Vendedores", abrir_vendedores, frame_ges)
    btn("   👥 Clientes", abrir_clientes, frame_ges)

    grupos["ges"] = frame_ges
    botones["ges"] = btn_ges

    # ===== REPORTES =====
    btn_rep = btn("▶ 👥 Centro/Reportes", lambda: mostrar("rep"), sidebar)
    frame_rep = tk.Frame(sidebar, bg="#111122")
    btn("   📒 Kardex", lambda: kardex.abrir_kardex(menu), frame_rep)
    btn(
        "   📊 Kardex General",
        lambda: kardex_general.abrir_kardex_general(menu),
        frame_rep,
    )
    btn("   📊 Kardex Total", lambda: kardex_total.abrir_kardex_total(menu), frame_rep)
    btn(
        "   📊 Inventario Valorizado",
        lambda: inventario_valorizado.abrir_inventario_valorizado(menu),
        frame_rep,
    )
    btn("   📊 Faltantes", lambda: abrir_reporte_faltantes(menu), frame_rep)
    btn("   📊 Movimientos", lambda: abrir_movimientos(menu), frame_rep)
    btn("   📊 Ventas x Vendedores", lambda: abrir_reporte_vendedores(menu), frame_rep)
    btn("   📊 Totales x Vendedor", lambda: abrir_reporte_totales_vendedores(menu), frame_rep)
    
    grupos["rep"] = frame_rep
    botones["rep"] = btn_rep

    # ===== CONFIGURACIÓN =====
    btn_conf = btn("▶ ⚙ Configuración", lambda: mostrar("conf"), sidebar)
    frame_conf = tk.Frame(sidebar, bg="#111122")

    btn("   🏢 Empresa", lambda: abrir_configuracion(menu), frame_conf)
    btn("   👥 Usuarios", lambda: usuarios_admin.abrir_usuarios(menu), frame_conf)
    btn("   💾 Backup", lambda: ejecutar_backup(), frame_conf)
    btn("   ♻️ Restaurar Backup", ejecutar_restaurar, frame_conf)
    
    grupos["conf"] = frame_conf
    botones["conf"] = btn_conf

    tk.Label(sidebar, bg="#111122").pack(expand=True)

    tk.Button(
        sidebar,
        text="🚪 Cerrar sesión",
        bg="#c0392b",
        fg="white",
        font=("Segoe UI", 8, "bold"),
        relief="flat",
        height=3,
        command=salir_completo,
    ).pack(fill="x", pady=8, padx=12)

    mostrar("op")


# ===================== APP PRINCIPAL =====================
conectar_db()

app = ctk.CTk()
app.title("Login de Entrada")
app.resizable(False, False)
app.config(bg="#2c2c44")

ancho = 420
alto = 610
x = (app.winfo_screenwidth() // 2) - (ancho // 2)
y = (app.winfo_screenheight() // 2) - (alto // 2)
app.geometry(f"{ancho}x{alto}+{x}+{y-30}")

if os.path.exists("icono.ico"):
    app.iconbitmap("icono.ico")

tk.Label(app, text="🔐", font=("Segoe UI Emoji", 100), bg="#2c2c44").pack(pady=5)

tk.Label(
    app,
    text="INICIO DE SESIÓN",
    fg="white",
    bg="#2c2c44",
    font=("Segoe UI", 20, "bold"),
).pack(pady=5)

card = tk.Frame(app, bg="#2c2c44", padx=30, pady=25)
card.pack(pady=10)

tk.Label(card, text="👤 Usuario", fg="white", bg="#2c2c44").pack(anchor="w")
entry_usuario = tk.Entry(card, width=28)
entry_usuario.pack(pady=5)

tk.Label(card, text="🔑 Contraseña", fg="white", bg="#2c2c44").pack(anchor="w")
entry_clave = tk.Entry(card, show="*", width=28)
entry_clave.pack(pady=5)

tk.Checkbutton(
    card,
    text="Mostrar contraseña",
    bg="#2c2c44",
    fg="white",
    selectcolor="#2c2c44",
    command=mostrar_clave,
).pack(pady=5)

tk.Button(
    app,
    text="🚀 INGRESAR",
    bg="#00a300",
    fg="white",
    width=25,
    height=2,
    command=validar_login,
).pack(pady=8)

tk.Label(
    app,
    text="Sistema de Gestión © 2025",
    fg="#aaaaaa",
    bg="#2c2c44",
    font=("Segoe UI", 9),
).pack(side="bottom", pady=1)

app.mainloop()

#en totales kardex mal totales

#pyinstaller --onedir --windowed --noupx main.py
#pyinstaller --onedir --windowed --add-data "logo.png;." main.py
#pyinstaller --onedir --windowed --noupx --name=WSoft main.py
#pyinstaller --onedir --windowed --noupx --name=WSoft --icon=logop.ico main.py
#pyinstaller --onedir --windowed --noupx --name=WSoft --icon=wsoft.ico --add-data "logos;logos" main.py  
