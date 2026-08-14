from core import *
from config import *
from models.movimientos_model import registrar_movimiento
from utils.busqueda_productos import buscar_producto_ui
from models.inventario_model import buscar_producto_db
from clientes import abrir_clientes
from vendedores import abrir_vendedores
from reportes.factura_venta import factura_venta
from reportes.utilidades import datos_empresa
from config import obtener_empresa
from reportes.utilidades import obtener_venta

def obtener_ruta_base():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = obtener_ruta_base()


DB_EMPRESA = os.path.join(
    BASE_DIR,
    "db",
    "empresa.db"
)

def obtener_config_impresion():

    conn = sqlite3.connect(DB_EMPRESA)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT impresion_venta,
               abrir_pdf_venta
        FROM empresa
        LIMIT 1
        """
    )

    data = cur.fetchone()

    conn.close()


    if data:
        return data[0], data[1]


    return "PREGUNTAR", 0


# ================== CLIENTE ==================
cliente_actual = {"codigo": "CF", "nombre": "CONSUMIDOR FINAL"}
vendedor_actual = {"codigo": "01", "nombre": "VENDEDOR ESTRELLA" }


# ================== UTILIDADES ==================
def formato_moneda(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def centrar(win, w, h):
    win.update_idletasks()
    x = (win.winfo_screenwidth() - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")


# ================== VENTAS ==================
#def abrir_ventas(parent):
def abrir_ventas(parent, refrescar=None):

    if getattr(parent, "ventas_abierto", False):
        return
    parent.ventas_abierto = True

    win = ctk.CTkToplevel(parent)
    win.title("Ventas")
    win.state("zoomed")
    win.grab_set()
    
    def cerrar():
        parent.ventas_abierto = False
        win.destroy()

        if refrescar:
            refrescar()

    win.protocol("WM_DELETE_WINDOW", cerrar)

    main = ctk.CTkFrame(win)
    main.pack(fill="both", expand=True, padx=15, pady=15)

    ctk.CTkLabel(main, text="🧾 PUNTO DE VENTA", font=("Segoe UI", 26, "bold")).pack(
        pady=10
    )

    # ================== CABECERA ==================

    tipo_pago = tk.StringVar(value="CONTADO")
    tipo_precio = tk.StringVar(value="DETAL")

    """ctk.CTkRadioButton(cab, text="Contado", variable=tipo_pago, value="CONTADO").pack(
        side="left", padx=10
    )
    ctk.CTkRadioButton(cab, text="Crédito", variable=tipo_pago, value="CREDITO").pack(
        side="left", padx=10
    )
    ctk.CTkRadioButton(cab, text="Detal", variable=tipo_precio, value="DETAL").pack(
        side="left", padx=20
    )
    ctk.CTkRadioButton(cab, text="Mayor", variable=tipo_precio, value="MAYOR").pack(
        side="left"
    )"""

    # ================== CLIENTE - VENDEDORES  ==================
    cliente_frame = ctk.CTkFrame(main)  
    cliente_frame.pack(fill="x", pady=5)

    lbl_cliente = ctk.CTkLabel(
        cliente_frame,
        text="CLIENTE: CF - CONSUMIDOR FINAL", font=("Segoe UI", 16, "bold"))
    lbl_cliente.pack(side="left", padx=10)
    
    vendedor_frame = ctk.CTkFrame(main)
    vendedor_frame.pack(fill="x", pady=5)

    lbl_vendedor = ctk.CTkLabel(
    vendedor_frame,
        text="VENDEDOR: 01 - VENDEDOR ESTRELLA",font=("Segoe UI",16,"bold"))
    lbl_vendedor.pack(side="left", padx=10)
    
    def recibir_vendedor(cod, nom):
        vendedor_actual["codigo"] = cod
        vendedor_actual["nombre"] = nom
        lbl_vendedor.configure(text=f"VENDEDOR: {cod} - {nom}")

    def seleccionar_vendedor():
        abrir_vendedores(win, modo="seleccion", callback=recibir_vendedor)

    def recibir_cliente(cod, nom):
        cliente_actual["codigo"] = cod
        cliente_actual["nombre"] = nom
        lbl_cliente.configure(text=f"CLIENTE: {cod} - {nom}")

    def seleccionar_cliente():
        abrir_clientes(win, modo="seleccion", callback=recibir_cliente)
        
    ctk.CTkButton(
        cliente_frame, text="🔍 VENDEDOR (F4)", command=seleccionar_vendedor
    ).pack(side="right", padx=5)
    ctk.CTkButton(
        cliente_frame, text="🔍 CLIENTE (F3)", command=seleccionar_cliente
    ).pack(side="right", padx=5)

    win.bind("<F4>", lambda e: seleccionar_vendedor())
    win.bind("<F3>", lambda e: seleccionar_cliente())    
    win.bind("<F2>", lambda e: ventana_cobro())

    # ================== BUSQUEDA ==================
    bus = ctk.CTkFrame(main)
    bus.pack(fill="x", pady=8)

    # FRAME DE TEXTOS
    lbl = ctk.CTkFrame(bus, fg_color="transparent")
    lbl.pack(fill="x")

    ctk.CTkLabel(lbl, text=" Abreviatura o Codigo para Buscar Producto").pack(
        side="left", padx=(5, 220)
    )
    ctk.CTkLabel(lbl, text="Cantidad").pack(side="left")

    # FRAME DE ENTRADAS
    inputs = ctk.CTkFrame(bus, fg_color="transparent")
    inputs.pack(fill="x")

    entry_buscar = ctk.CTkEntry(inputs, width=420, justify="left")
    entry_buscar.pack(side="left", padx=10)

    entry_cant = ctk.CTkEntry(inputs, width=100, justify="center")
    entry_cant.pack(side="left")

    entry_cant.insert(0, "1")

    # ================== TREE BUSQUEDA ==================
    cols = ("codigo", "descripcion", "existencia", "precio", "impuesto")
    tree_bus = ttk.Treeview(main, columns=cols, show="headings", height=5)

    for c in cols:
        tree_bus.heading(c, text=c.upper())
        tree_bus.column(c, anchor="center", width=160)

    tree_bus.pack(fill="x", padx=10)

    # ================== DETALLE ==================
    cols_v = ("codigo", "descripcion", "cantidad", "precio", "subtotal")
    tree_det = ttk.Treeview(main, columns=cols_v, show="headings", height=9)

    for c in cols_v:
        tree_det.heading(c, text=c.upper())
        tree_det.column(c, anchor="center", width=160)

    tree_det.pack(fill="both", expand=True, padx=10, pady=5)

    # ================== LOGICA ==================
    carrito = []
    producto_sel = {}

    entry_buscar.bind(
        "<KeyRelease>",
        lambda e: buscar_producto_ui(
            entry_buscar=entry_buscar,
            tree_bus=tree_bus,
            buscar_producto_db=buscar_producto_db,
            # ❌ sin botón
            # ❌ sin permitir_crear
        ),
    )

    def buscar_producto(_=None):

        conn = sqlite3.connect(DB_INV)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT codigo, descripcion, cantidad,
            CASE WHEN ?='DETAL' THEN precio_detal ELSE precio_mayor END,
            impuesto
            FROM inventario
            WHERE
                codigo = ?
                OR codigo LIKE ?
                OR descripcion LIKE ?
                OR descripcion LIKE ?
            ORDER BY
                CASE
                    WHEN codigo = ? THEN 1
                    WHEN codigo LIKE ? THEN 2
                    WHEN descripcion LIKE ? THEN 3
                    ELSE 4
                END
            LIMIT 20
        """,
            (
                tipo_precio.get(),
                txt,
                f"{txt}%",
                f"{txt}%",
                f"%{txt}%",
                txt,
                f"{txt}%",
                f"{txt}%",
            ),
        )

        for fila in cur.fetchall():
            tree_bus.insert("", "end", values=fila)

        conn.close()

    def ir_a_tree(_=None):
        hijos = tree_bus.get_children()
        if not hijos:
            return
        tree_bus.focus_set()
        tree_bus.selection_set(hijos[0])
        tree_bus.focus(hijos[0])

    def seleccionar_producto(_=None):
        item = tree_bus.focus()
        vals = tree_bus.item(item, "values")

        if not vals or vals[0] == "":
            return

        # Mostrar producto elegido en la caja de búsqueda
        codigo, desc, stock, precio, impuesto = tree_bus.item(item, "values")

        # volver a consultar impuesto real del producto
        conn = sqlite3.connect(DB_INV)
        cur = conn.cursor()
        cur.execute("SELECT impuesto FROM inventario WHERE codigo = ?", (codigo,))
        imp_row = cur.fetchone()
        conn.close()

        impuesto_producto = float(imp_row[0]) / 100 if imp_row else 0

        entry_buscar.delete(0, tk.END)
        entry_buscar.insert(0, desc)

        stock = float(stock)
        if int(stock) <= 0:
            messagebox.showwarning("Stock", "Producto sin existencia")
            # limpiar búsqueda
            entry_buscar.delete(0, tk.END)
            producto_sel.clear()
            # volver a buscar
            entry_buscar.focus_force()
            return

        producto_sel.clear()
        producto_sel.update(
            {
                "codigo": codigo,
                "descripcion": desc,
                "precio": float(precio),
                "stock": int(stock),
                "impuesto": float(impuesto),  # 👈 IMPORTANTE
            }
        )

        entry_cant.focus()
        entry_cant.select_range(0, tk.END)

    def agregar_producto(_=None):
        if not producto_sel:
            return

        try:
            cant = int(entry_cant.get())
        except ValueError:
            return

        precio = float(producto_sel["precio"])
        impuesto_porcentaje = float(producto_sel["impuesto"])  # ejemplo: 19

        sub = cant * precio
        impuesto = sub * (impuesto_porcentaje / 100)

        carrito.append(
            {
                "codigo": producto_sel["codigo"],
                "descripcion": producto_sel["descripcion"],
                "cantidad": cant,
                "precio": precio,
                "subtotal": sub,
                "impuesto": impuesto_porcentaje,      # 16
                "impuesto_monto": impuesto,           # 168.00
            }
        )

        tree_det.insert(
            "",
            "end",
            values=(
                producto_sel["codigo"],
                producto_sel["descripcion"],
                cant,
                formato_moneda(producto_sel["precio"]),
                formato_moneda(sub),
            ),
        )

        producto_sel.clear()
        entry_buscar.delete(0, tk.END)
        entry_cant.delete(0, tk.END)
        entry_cant.insert(0, "1")
        calcular_totales()
        entry_buscar.focus_set()

    # ================== TOTALES ==================
    frame_totales = ctk.CTkFrame(main)
    frame_totales.pack(fill="x", pady=10)

    entry_sub = ctk.CTkEntry(frame_totales, width=160, justify="right")
    entry_imp = ctk.CTkEntry(frame_totales, width=160, justify="right")
    entry_tot = ctk.CTkEntry(
        frame_totales, width=180, justify="right", font=("Segoe UI", 20, "bold")
    )

    for txt, ent in (
        ("SUBTOTAL", entry_sub),
        ("IMPUESTO", entry_imp),
        ("TOTAL", entry_tot),
    ):
        ctk.CTkLabel(frame_totales, text=txt, font=("Segoe UI", 16, "bold")).pack(
            side="right", padx=5
        )

        ent.pack(side="right", padx=10)

    def calcular_totales():
        subtotal = sum(i["subtotal"] for i in carrito)
        impuesto_total = sum(i["impuesto"] for i in carrito)
        total_general = subtotal + impuesto_total

        entry_sub.delete(0, tk.END)
        entry_imp.delete(0, tk.END)
        entry_tot.delete(0, tk.END)

        entry_sub.insert(0, formato_moneda(subtotal))
        entry_imp.insert(0, formato_moneda(impuesto_total))
        entry_tot.insert(0, formato_moneda(total_general))

    def calcular_totales():
        subtotal = sum(i["subtotal"] for i in carrito)
        impuesto_total = sum(i["impuesto"] for i in carrito)
        total_general = subtotal + impuesto_total

        entry_sub.delete(0, tk.END)
        entry_imp.delete(0, tk.END)
        entry_tot.delete(0, tk.END)

        entry_sub.insert(0, formato_moneda(subtotal))
        entry_imp.insert(0, formato_moneda(impuesto_total))
        entry_tot.insert(0, formato_moneda(total_general))

    # ================== BINDS ==================
    entry_buscar.bind("<KeyRelease>", buscar_producto)
    entry_buscar.bind("<Down>", ir_a_tree)
    tree_bus.bind("<Return>", seleccionar_producto)
    entry_cant.bind("<Return>", agregar_producto)
    win.bind("<Escape>", lambda e: cerrar())
    

    win.after(
        150,
        lambda: entry_buscar.focus_set()
        if entry_buscar.winfo_exists()
        else None
    )
    #win.after(150, entry_buscar.focus_set() if entry_buscar.winfo_exists() else None)

    # ================== QUITAR PRODUCTO ==================
    def quitar_producto():
        sel = tree_det.selection()
        if not sel:
            return

        idx = tree_det.index(sel[0])
        tree_det.delete(sel[0])
        carrito.pop(idx)
        calcular_totales()

    # ================== LIMPIAR VENTA ==================
    def limpiar_venta():
        carrito.clear()
        producto_sel.clear()
        tree_det.delete(*tree_det.get_children())
        tree_bus.delete(*tree_bus.get_children())

        for e in (entry_sub, entry_imp, entry_tot):
            e.delete(0, tk.END)

        entry_buscar.delete(0, tk.END)
        entry_cant.delete(0, tk.END)
        entry_cant.insert(0, "1")

        cliente_actual.update({"codigo": "CF", "nombre": "CONSUMIDOR FINAL"})
        lbl_cliente.configure(text="CLIENTE: CF - CONSUMIDOR FINAL")
        entry_buscar.focus_set()

    # ================== COBRO ==================
    def ventana_cobro():
        if not carrito:
            messagebox.showwarning("Cobro", "No hay productos")
            return

        subtotal = sum(i["subtotal"] for i in carrito)
        impuesto = sum(i["impuesto"] for i in carrito)
        total = subtotal + impuesto

        confirmar_final = False  # doble confirmación

        cobro = ctk.CTkToplevel(win)
        cobro.title("Cobro")
        cobro.transient(win)
        cobro.grab_set()
        # ===== CONTENEDOR =====
        centrar(cobro, 500, 580)
        frame = ctk.CTkFrame(cobro)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.pack_propagate(False)  # 👈 CLAVE

        # ===== TITULO =====
        ctk.CTkLabel(
            frame, text="💰 COBRO DE FACTURA", font=("Segoe UI", 34, "bold")
        ).pack(anchor="e", pady=(0, 10))

        # ===== TOTAL =====
        ctk.CTkLabel(frame, text="TOTAL", font=("Segoe UI", 50, "bold")).pack(
            anchor="e"
        )
        lbl_total = ctk.CTkLabel(
            frame,
            text=formato_moneda(total),
            font=("Segoe UI", 60, "bold"),
            text_color="#FD640B",
        )
        lbl_total.pack(anchor="e", pady=(0, 20))

        # ===== PAGO =====
        ctk.CTkLabel(frame, text="PAGO", font=("Segoe UI", 50, "bold")).pack(anchor="e")

        entry_pago = ctk.CTkEntry(
            frame, height=80, font=("Segoe UI", 50, "bold"), justify="right"
        )
        entry_pago.pack(fill="x", pady=(5, 20))
        entry_pago.focus_force()

        lbl_vuelto = ctk.CTkLabel(frame, text="$ 0,00", font=("Segoe UI", 50, "bold"))
        lbl_vuelto.pack(anchor="e", pady=(5, 20))

        # ===== LOGICA =====
        confirmar_final = False

        def calcular_vuelto(_=None):
            nonlocal confirmar_final
            confirmar_final = False

            try:
                pago = float(entry_pago.get())
                vuelto = pago - total
                if vuelto >= 0:
                    lbl_vuelto.configure(
                        text=f"VUELTO: {formato_moneda(vuelto)}", text_color="#F7E705"
                    )
                else:
                    lbl_vuelto.configure(text="VUELTO: 0,00", text_color="red")
            except ValueError:
                lbl_vuelto.configure(text="VUELTO: 0,00", text_color="gray")

            btn_confirmar.configure(text="CONFIRMAR ⏎")

        def confirmar(_=None):
            nonlocal confirmar_final

            try:
                pago = float(entry_pago.get())
            except ValueError:
                return

            if pago < total:
                messagebox.showwarning("Cobro", "Pago insuficiente")
                return

            # PRIMER ENTER
            if not confirmar_final:
                confirmar_final = True
                btn_confirmar.configure(
                    text="CONFIRMAR VENTA ⏎", fg_color="#C0392B", hover_color="#922B21"
                )
                return

            # SEGUNDO ENTER → FINALIZA
            cobro.destroy()
            guardar_venta(pago)

        # ===== BOTONES =====
        btns = ctk.CTkFrame(frame)
        btns.pack(fill="x", pady=10)

        btn_confirmar = ctk.CTkButton(
            btns, text="CONFIRMAR ⏎", font=("Segoe UI", 16, "bold"), command=confirmar
        )
        btn_confirmar.pack(side="right", padx=5)

        ctk.CTkButton(btns, text="CANCELAR Esc", command=cobro.destroy).pack(
            side="right", padx=5
        )

        # ===== BINDS =====

        entry_pago.bind("<KeyRelease>", calcular_vuelto)
        entry_pago.bind("<Return>", lambda e: btn_confirmar.focus_set())
        btn_confirmar.bind("<Return>", confirmar)
        cobro.bind("<Escape>", lambda e: cobro.destroy())
        
        def poner_foco_pago():
            try:
                if cobro.winfo_exists() and entry_pago.winfo_exists():
                    entry_pago.focus_force()
            except tk.TclError:
                pass

        cobro.after(100, poner_foco_pago)
        
    # ================== GUARDAR VENTA ==================

    def guardar_venta(pago):
        
        from tkinter import messagebox
        #messagebox.showinfo("DEBUG", "Entró a guardar_venta")
        
        conn_v = sqlite3.connect(DB_VENTAS)
        conn_i = sqlite3.connect(DB_INV)

        cur_v = conn_v.cursor()
        cur_i = conn_i.cursor()

        subtotal = sum(i["subtotal"] for i in carrito)
        impuesto = sum(i["impuesto_monto"] for i in carrito)
        total = subtotal + impuesto
        vuelto = pago - total

        # 1️⃣ Guardar venta
        cur_v.execute(
            """
            INSERT INTO ventas
            (fecha, tipo_pago, tipo_precio, subtotal, impuesto, total,
            cliente_codigo, cliente_nombre, vendedor_codigo)
            VALUES (?,?,?,?,?,?,?,?,?)
        """,
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                tipo_pago.get(),
                tipo_precio.get(),
                subtotal,
                impuesto,
                total,
                cliente_actual["codigo"],
                cliente_actual["nombre"],
                vendedor_actual["codigo"],
            ),
        )
        #messagebox.showinfo("DEBUG", "Insertó venta")
        id_venta = cur_v.lastrowid
        #messagebox.showinfo("DEBUG", f"id_venta = {id_venta}")
        #print(f"ID insertado: {id_venta}")

        # 2️⃣ Recorrer carrito
        
        #messagebox.showinfo("DEBUG", "Va a insertar detalle")
        for i in carrito:

            cur_v.execute(
                """
                INSERT INTO detalle_venta
                (
                    id_venta,
                    codigo,
                    descripcion,
                    cantidad,
                    precio,
                    impuesto_porcentaje,
                    impuesto_monto,
                    subtotal
                )
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    id_venta,
                    i["codigo"],
                    i["descripcion"],
                    i["cantidad"],
                    i["precio"],
                    i["impuesto"],          # porcentaje (16, 21, 0...)
                    i["impuesto_monto"],    # monto calculado
                    i["subtotal"],
                )
            )
        
            # Descontar inventario
            cur_i.execute(
                """
                UPDATE inventario
                SET cantidad = cantidad - ?
                WHERE codigo = ?
            """,
                (
                    i["cantidad"],
                    i["codigo"],
                ),
            )

            registrar_movimiento(
                producto_id=i["codigo"],
                tipo="VENTA",
                cantidad=i["cantidad"],
                referencia=f"VENTA {id_venta}",
            )

        conn_v.commit()
        conn_i.commit()

        modo, abrir_pdf = obtener_config_impresion()


        if modo == "PREGUNTAR":

            ventana_documentos(
                cliente_actual,
                carrito,
                id_venta,
                subtotal,
                impuesto,
                total,
                pago,
                vuelto
            )


        elif modo == "TICKET":

            generar_ticket(
                id_venta,
                subtotal,
                impuesto,
                total,
                pago,
                vuelto
            )

            messagebox.showinfo(
                "Venta completada",
                "Ticket generado correctamente."
            )

            limpiar_venta()


        elif modo == "FACTURA":
            
            archivo = factura_venta(
                id_venta
            )

            if abrir_pdf:
                #print("PDF generado:", archivo)
                os.startfile(archivo)

            messagebox.showinfo(
                "Venta completada",
                "Factura generada correctamente."
            )

            limpiar_venta()


        elif modo == "NADA":

            limpiar_venta()


    # ================== TICKET ==================

    def generar_ticket(id_venta, sub, imp, tot, pago, vuelto):

        cliente_actual, carrito, _, _, _ = obtener_venta(id_venta)
        #cliente_actual, carrito = obtener_venta(id_venta)

        empresa = datos_empresa()

        nombre = empresa["nombre"]
        direccion = empresa["direccion"]
        telefono = empresa["telefono"]
        rif = empresa.get("rif", "")

        os.makedirs("tickets", exist_ok=True)

        ANCHO = 32  # 58mm (40 si usas impresora 80mm)

        with open(f"tickets/ticket_{id_venta}.txt", "w", encoding="utf-8") as f:

            # ===== ENCABEZADO =====

            f.write(f"VENTA #: {id_venta}\n")
            f.write(datetime.now().strftime("%d/%m/%Y %H:%M\n"))

            f.write(nombre.center(ANCHO) + "\n")
            f.write(direccion.center(ANCHO) + "\n")
            f.write(f"TEL: {telefono}".center(ANCHO) + "\n")
            f.write(f"RIF: {rif}".center(ANCHO) + "\n")

            f.write(
                f"CLIENTE: {cliente_actual['codigo']} - {cliente_actual['nombre']}\n"
            )

            f.write("_" * ANCHO + "\n")

            # ===== PRODUCTOS =====
            for i in carrito:

                desc = i["descripcion"][:19]
                cant = f"{i['cantidad']:>3}"
                total = f"{formato_moneda(i['subtotal']):>9}"

                f.write(f"{desc:<19}{cant} {total}\n")

            f.write("\n")

            # ===== TOTALES =====
            f.write(f"{'SUBTOTAL:':<12}{formato_moneda(sub):>20}\n")
            f.write(f"{'IMPUESTO:':<12}{formato_moneda(imp):>20}\n")
            f.write(f"{'TOTAL:':<12}{formato_moneda(tot):>20}\n")
            f.write(f"{'PAGO:':<12}{formato_moneda(pago):>20}\n")
            f.write(f"{'VUELTO:':<12}{formato_moneda(vuelto):>20}\n")

            f.write("\n")
            f.write("GRACIAS POR SU COMPRA".center(ANCHO) + "\n")

    ################################################
    def ventana_documentos(
        cliente_actual, carrito, id_venta, subtotal, impuesto, total, pago, vuelto
    ):

        carrito_venta = carrito.copy()

        win = ctk.CTkToplevel()
        win.title("Documentos")
        win.geometry("420x200")

        barra = ctk.CTkFrame(win)
        barra.pack(side="right", fill="y", padx=10, pady=10)

        ctk.CTkButton(
            barra, text="Factura", command=lambda: factura_venta(id_venta)
        ).pack(fill="x", pady=5)

        ctk.CTkButton(
            barra,
            text="Ticket",
            command=lambda: generar_ticket(
                id_venta,
                subtotal,
                impuesto,
                total,
                pago,
                vuelto,
            ),
        ).pack(fill="x", pady=5)

        def continuar():
            limpiar_venta()
            win.destroy()

        ctk.CTkButton(barra, text="Continuar", command=continuar).pack(
            fill="x", pady=20
        )

    # ================== BOTONES ==================
    btns = ctk.CTkFrame(main)
    btns.pack(fill="x", pady=15)

    ctk.CTkButton(
        btns,
        text="💰 f2 COBRAR",
        width=240,
        height=60,
        font=("Segoe UI", 18, "bold"),
        command=ventana_cobro,
    ).pack(side="left", padx=10)

    ctk.CTkButton(
        btns,
        text="🗑️ QUITAR",
        width=240,
        height=60,
        font=("Segoe UI", 18, "bold"),
        command=quitar_producto,
    ).pack(side="left", padx=10)

    ctk.CTkButton(
        btns,
        text="🧹 LIMPIAR",
        width=240,
        height=60,
        font=("Segoe UI", 18, "bold"),
        command=limpiar_venta,
    ).pack(side="left", padx=10)

    ctk.CTkButton(
        btns,
        text="❌ SALIR",
        width=240,
        height=60,
        font=("Segoe UI", 18, "bold"),
        command=cerrar,
    ).pack(side="right", padx=10)

    # ================== BINDS EXTRA ==================
    tree_det.bind("<Delete>", lambda e: quitar_producto())
