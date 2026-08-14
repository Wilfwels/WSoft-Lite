from core import *
from config import *
from models.movimientos_model import registrar_movimiento
from proveedores import abrir_proveedores
from inventario import abrir_inventario
from utils.busqueda_productos import buscar_producto_ui
from reportes.plantilla import crear_documentoc
from reportes.utilidades import siguiente_consecutivoe, siguiente_consecutivos

# ================== PROVEEDOR ==================
proveedor_actual = {"codigo": "CF", "nombre": "PROVEEDOR FINAL"}

# ================== UTILIDADES ==================
def formato_moneda(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def centrar(win, w, h):
    win.update_idletasks()
    x = (win.winfo_screenwidth() - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")


# ================== COMPRAS ==================
def abrir_compras(parent, modo="COMPRA", refrescar=None):

    if getattr(parent, "compras_abierto", False):
        return
    parent.compras_abierto = True

    win = ctk.CTkToplevel(parent)
    win.title("Compras")
    win.state("zoomed")
    win.grab_set()
    
    def cerrar():
        parent.compras_abierto = False
        win.destroy()

        if refrescar:
            refrescar()
            
    win.protocol("WM_DELETE_WINDOW", cerrar)
    
    CONFIG = {
        "COMPRA": {
            "mov_tipo": "COMPRA",
            "referencia": "COMPRA",
            "usa_proveedor": True,
            "usa_cobro": True,
            "afecta": +1,
            "usa_compras": True,
        },
        "ENTRADA": {
            "mov_tipo": "COMPRA",
            "referencia": "ENTRADA X INVENTARIO",
            "usa_proveedor": True,
            "usa_cobro": False,
            "afecta": +1,
            "usa_compras": True,
        },
        "SALIDA": {
            "mov_tipo": "VENTA",
            "referencia": "SALIDA",
            "usa_proveedor": True,
            "use_cobro": False,
            "afecta": +1,
            "usa_compras": True,
        },
    }

    CONFIG = {
        "COMPRA": {
            "titulo": "PUNTO DE COMPRAS",
            "factor": +1,
            "usa_proveedor": True,
            "usa_cobro": True,
            "mov_tipo": "COMPRA",
        },
        "ENTRADA": {
            "titulo": "ENTRADA DE INVENTARIO",
            "factor": +1,
            "usa_proveedor": False,
            "usa_cobro": False,
            "mov_tipo": "ENTRADA MANUAL",
        },
        "SALIDA": {
            "titulo": "SALIDA DE INVENTARIO",
            "factor": +1,
            "usa_proveedor": False,
            "usa_cobro": False,
            "mov_tipo": "SALIDA MANUAL",
        },
    }

    cfg = CONFIG.get(modo, CONFIG["COMPRA"])

    win.protocol("WM_DELETE_WINDOW", cerrar)

    main = ctk.CTkFrame(win)
    main.pack(fill="both", expand=True, padx=15, pady=15)

    ctk.CTkLabel(main, text=cfg["titulo"], font=("Segoe UI", 26, "bold")).pack(pady=10)

    def producto_creado(prod):
        # prod llega desde inventario

        producto_sel.clear()
        producto_sel.update(
            {
                "codigo": prod["codigo"],
                "descripcion": prod["descripcion"],
                "costo": float(prod["costo"]),
                "stock": 0,
                "impuesto": float(prod["impuesto"]),
            }
        )

        # limpiar resultados anteriores
        tree_bus.delete(*tree_bus.get_children())

        # insertar producto creado
        tree_bus.insert(
            "",
            "end",
            values=(
                prod["codigo"],
                prod["descripcion"],
                0,
                prod["costo"],
                prod["impuesto"],
            ),
        )

        # seleccionar automáticamente
        item = tree_bus.get_children()[0]
        tree_bus.focus(item)
        tree_bus.selection_set(item)

        # simular Enter (pasar a cantidad)
        seleccionar_producto()

        entry_cant.focus_set()
        entry_cant.select_range(0, "end")

    def crear_producto_desde_compras(event=None):
        abrir_inventario(win, modo="crear", callback=producto_creado)

    # ================== CABECERA ==================
    cab = ctk.CTkFrame(main)
    cab.pack(fill="x", pady=5)

    tipo_pago = tk.StringVar(value="CONTADO")

    ctk.CTkRadioButton(cab, text="          ", variable=tipo_pago, value="CONTADO").pack(
        side="left", padx=10
    )
    ctk.CTkRadioButton(cab, text="          ", variable=tipo_pago, value="CREDITO").pack(
        side="left", padx=10
    )

    # ==================  PROVEEDOR ==================
    proveedor_frame = ctk.CTkFrame(main)
    proveedor_frame.pack(fill="x", pady=5)
    if not cfg["usa_proveedor"]:
        proveedor_frame.pack_forget()

    lbl_proveedor = ctk.CTkLabel(
        proveedor_frame,
        text="PROVEEDOR: PF - PROVEEDOR FINAL",
        font=("Segoe UI", 16, "bold"),
    )
    lbl_proveedor.pack(side="left", padx=10)

    def recibir_proveedor(cod, nom):
        print("RECIBIDO:", cod, nom)
        proveedor_actual["codigo"] = cod
        proveedor_actual["nombre"] = nom
        lbl_proveedor.configure(text=f"PROVEEDOR: {cod} - {nom}")

    def seleccionar_proveedor():
        abrir_proveedores(win, modo="seleccion", callback=recibir_proveedor)

    ctk.CTkButton(
        proveedor_frame, text="🔍 PROVEEDOR (F3)", command=seleccionar_proveedor
    ).pack(side="right", padx=5)

    btn_producto = ctk.CTkButton(
        proveedor_frame,
        text="📦 PRODUCTO (F4)",
        fg_color="#c0392b",  # rojo fuerte
        hover_color="#e74c3c",
        text_color="white",
        font=("Segoe UI", 14, "bold"),
        command=crear_producto_desde_compras,
    )

    btn_producto.pack(side="left", padx=8)
    btn_producto.pack_forget()  # 👈 oculto al iniciar

    win.bind("<F3>", lambda e: seleccionar_proveedor())
    win.bind("<F4>", crear_producto_desde_compras)

    def accion_principal(event=None):

        if not carrito:
            messagebox.showwarning("Proceso", "No hay productos")
            return

        # 🧾 SOLO EN COMPRA abre cobro
        if cfg["usa_cobro"]:
            ventana_cobro()
            return

        # 📥📤 ENTRADA / SALIDA → confirmar directo
        confirmar = messagebox.askyesno(
            "Confirmar movimiento",
            f"{cfg['mov_tipo']}\n\n¿Seguro desea procesar este movimiento?",
        )

        if confirmar:
            guardar_compra(0)

    win.bind("<F2>", accion_principal)

    # ================== BUSQUEDA ==================
    bus = ctk.CTkFrame(main)
    bus.pack(fill="x", pady=8)

    # FRAME DE TEXTOS
    lbl = ctk.CTkFrame(bus, fg_color="transparent")
    lbl.pack(fill="x")

    ctk.CTkLabel(lbl, text=" Abreviatura o Codigo para Buscar Producto").pack(side="left", padx=(5, 220))
    ctk.CTkLabel(lbl, text="Cantidad").pack(side="left", padx=(15,50))
    ctk.CTkLabel(lbl, text="Costo").pack(side="left", padx=(5,50))

    # FRAME DE ENTRADAS
    inputs = ctk.CTkFrame(bus, fg_color="transparent")
    inputs.pack(fill="x")

    entry_buscar = ctk.CTkEntry(inputs, width=420, justify="left")
    entry_buscar.pack(side="left", padx=10)

    entry_cant = ctk.CTkEntry(inputs, width=100, justify="center")
    entry_cant.pack(side="left", padx=10)
    
    entry_cost = ctk.CTkEntry(inputs, width=100, justify="center")
    entry_cost.pack(side="left", padx=10)
    
    # ================== TREE BUSQUEDA ==================
    cols = ("codigo", "descripcion", "existencia", "costo", "impuesto")
    tree_bus = ttk.Treeview(main, columns=cols, show="headings", height=5)

    for c in cols:
        tree_bus.heading(c, text=c.upper())
        tree_bus.column(c, anchor="center", width=160)

    tree_bus.pack(fill="x", padx=10)

    # ================== DETALLE ==================
    cols_c = ("codigo", "descripcion", "cantidad", "costo", "subtotal")
    tree_det = ttk.Treeview(main, columns=cols_c, show="headings", height=9)

    for c in cols_c:
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
            btn_producto=btn_producto,
            permitir_crear=True,
        ),
    )

    def buscar_producto_db(txt):
        conn = sqlite3.connect(DB_INV)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT codigo, descripcion, cantidad, costo, impuesto
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
                txt,
                f"{txt}%",
                f"{txt}%",
                f"%{txt}%",
                txt,
                f"{txt}%",
                f"{txt}%",
            ),
        )

        resultados = cur.fetchall()
        conn.close()
        return resultados

    def ir_a_tree(_=None):
        hijos = tree_bus.get_children()
        if not hijos:
            return
        tree_bus.focus_set()
        tree_bus.selection_set(hijos[0])
        tree_bus.focus(hijos[0])

    # ================== SELECCIONAR PRODUCTO ==================

    def seleccionar_producto(event=None):
        item = tree_bus.focus()
        if not item:
            return "break"

        codigo, desc, stock, costo, impuesto = tree_bus.item(item, "values")

        producto_sel.clear()
        producto_sel.update(
            {
                "codigo": codigo,
                "descripcion": desc,
                "costo": float(costo),
                "stock": float(stock),
                "impuesto": float(impuesto),
            }
        )

        # 👉 NUEVO: reflejar selección en búsqueda
        
        entry_buscar.delete(0, tk.END)
        entry_buscar.insert(0, f"{codigo} - {desc}")

        entry_cost.delete(0, tk.END)
        entry_cost.insert(0, costo)
        
        entry_cant.focus()
        entry_cant.select_range(0, tk.END)        
        
        return "break"

    # ================== AGREGAR PRODUCTO ==================

    def agregar_producto(_=None):
        if not producto_sel:
            return

        try:
            cant = int(entry_cant.get())
            if cant <= 0:
                return
        except ValueError:
            return

        codigo = producto_sel["codigo"]
        costo = float(entry_cost.get() or 0)
        impuesto_pct = float(producto_sel["impuesto"])

        # 🔎 verificar si ya existe en carrito
        for i in carrito:
            if i["codigo"] == codigo:
                i["cantidad"] += cant
                i["subtotal"] = i["cantidad"] * costo
                i["impuesto"] = i["subtotal"] * (impuesto_pct / 100)

                # actualizar tree
                for item in tree_det.get_children():
                    if tree_det.item(item, "values")[0] == codigo:
                        tree_det.item(
                            item,
                            values=(
                                codigo,
                                i["descripcion"],
                                i["cantidad"],
                                formato_moneda(costo),
                                formato_moneda(i["subtotal"]),
                            ),
                        )
                        break

                calcular_totales()  # ✅ FALTABA
                limpiar_despues_agregar()  # ✅ UNA SOLA VEZ
                return

        # ➕ producto nuevo
        sub = cant * costo
        imp = sub * (impuesto_pct / 100)

        carrito.append(
            {
                "codigo": codigo,
                "descripcion": producto_sel["descripcion"],
                "cantidad": cant,
                "costo": costo,
                "subtotal": sub,
                "impuesto": imp,
            }
        )

        tree_det.insert(
            "",
            "end",
            values=(
                codigo,
                producto_sel["descripcion"],
                cant,
                formato_moneda(costo),
                formato_moneda(sub),
            ),
        )

        calcular_totales()  # ✅ BIEN UBICADO
        limpiar_despues_agregar()  # ✅ SIN DUPLICAR

    # ================== LIMPIEZA POST AGREGAR ==================
    def limpiar_despues_agregar():
        producto_sel.clear()
        entry_buscar.delete(0, tk.END)
        entry_cant.delete(0, tk.END)
        entry_cost.delete(0, tk.END)
        calcular_totales()
        entry_buscar.focus_set()
        producto_sel.clear()  # ⬅️ AL FINAL

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

    # ================== TOTALES ==================

    def calcular_totales():

        # 🔵 Solo calcular si es compra
        if not cfg["usa_cobro"]:
            entry_sub.delete(0, tk.END)
            entry_imp.delete(0, tk.END)
            entry_tot.delete(0, tk.END)
            return

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
    entry_buscar.bind("<Down>", ir_a_tree)
    tree_bus.bind("<Return>", seleccionar_producto)
    entry_cant.bind("<Return>",lambda e: (entry_cost.focus_set(),entry_cost.select_range(0, tk.END)))
    entry_cost.bind("<Return>", agregar_producto)
    
    win.bind("<Escape>", lambda e: cerrar())

    win.after(150, entry_buscar.focus_set)

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
        if tree_det and tree_det.winfo_exists():
            hijos = tree_det.get_children()
            if hijos:
                tree_det.delete(*hijos)

        for e in (entry_sub, entry_imp, entry_tot):
            e.delete(0, tk.END)

        entry_buscar.delete(0, tk.END)
        entry_cost.delete(0, tk.END)
        entry_cant.delete(0, tk.END)

        proveedor_actual.update({"codigo": "PF", "nombre": "CONSUMIDOR FINAL"})
        lbl_proveedor.configure(text="PROVEEDOR: PF - CONSUMIDOR FINAL")
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
                    text="CONFIRMAR COMPRA ⏎", fg_color="#C0392B", hover_color="#922B21"
                )
                return

            # SEGUNDO ENTER → FINALIZA
            guardar_compra(pago)
            cobro.destroy()

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

        cobro.after(100, lambda: entry_pago.focus_force())

    # ================== GUARDAR COMPRAS ==================

    def guardar_compra(pago):

        conn_c = sqlite3.connect(DB_COMPRAS)
        conn_i = sqlite3.connect(DB_INV)
        conn_e = sqlite3.connect(DB_ENTRADAS)
        conn_s = sqlite3.connect(DB_SALIDAS)
        conn_m = sqlite3.connect(DB_MOVIMI)
        
        cur_c = conn_c.cursor()
        cur_i = conn_i.cursor()
        cur_e = conn_e.cursor()
        cur_s = conn_s.cursor()
        cur_m = conn_m.cursor()
        
        subtotal = sum(i["subtotal"] for i in carrito)
        impuesto = sum(i["impuesto"] for i in carrito)
        total = subtotal + impuesto

        id_compra = None  # 👈 importante

        # =====================================================================
        # 🔵 SOLO SI ES COMPRA
        # =====================================================================
        if modo == "COMPRA":

            cur_c.execute(
                """
                INSERT INTO compras
                (fecha, proveedor_codigo, proveedor_nombre, subtotal, impuesto, total)
                VALUES (?,?,?,?,?,?)
                """,
                (
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    proveedor_actual["codigo"],
                    proveedor_actual["nombre"],
                    subtotal,
                    impuesto,
                    total,
                ),
            )
            conn_c.commit()
            
            id_compra = cur_c.lastrowid

            # 🔵 RECORRER CARRITO

            for i in carrito:

                # ===========================
                # GUARDAR DETALLE COMPRA
                # ===========================

                cur_c.execute(
                    """
                    INSERT INTO detalle_compra
                    (id_compra, codigo, descripcion, cantidad, costo, subtotal)
                    VALUES (?,?,?,?,?,?)
                    """,
                    (
                        id_compra,
                        i["codigo"],
                        i["descripcion"],
                        i["cantidad"],
                        i["costo"],
                        i["subtotal"],
                    ),
                )

                # ===========================
                # ACTUALIZAR INVENTARIO
                # ===========================

                cur_i.execute(
                    """
                    UPDATE inventario
                    SET cantidad = cantidad + ?,
                        costo = ?
                    WHERE codigo = ?
                    """,
                    (
                        i["cantidad"] * cfg["factor"],
                        i["costo"],
                        i["codigo"],
                    ),
                )

                # ===========================
                # REGISTRAR MOVIMIENTO
                # ===========================

                registrar_movimiento(
                    producto_id=i["codigo"],
                    tipo=cfg["mov_tipo"],
                    cantidad=i["cantidad"] * cfg["factor"],
                    referencia=cfg["titulo"],
                )

            # ===========================
            # GUARDAR CAMBIOS
            # ===========================

            conn_c.commit()
            conn_i.commit()
            conn_m.commit()

            # ===========================
            # CERRAR CONEXIONES
            # ===========================

            conn_c.close()
            conn_i.close()
            conn_m.close()

            items = []

            for p in carrito:
                items.append(
                    {
                        "codigo": p["codigo"],
                        "producto": p["descripcion"],
                        "cantidad": p["cantidad"],
                        "precio": p["costo"],
                        "total": p["subtotal"],
                    }
                )

            archivo = f"documentos/facturas_compra/compra_{id_compra:05d}.pdf"

            crear_documentoc(
                "FACTURA DE COMPRA",
                id_compra,
                proveedor_actual["nombre"],
                items,
                archivo,
            )
                
            messagebox.showinfo("Compra", f"Compra #{id_compra} registrada")

        # ===================== FIN DE COMPRA

        # =====================================================================
        # 🔵 SOLO SI ES ENTRADA DE INVENTARIO
        # =====================================================================
        if modo == "ENTRADA":
            
            cur_e.execute(
                """
                INSERT INTO compras
                (fecha, proveedor_codigo, proveedor_nombre, subtotal, impuesto, total)
                VALUES (?,?,?,?,?,?)
                """,
                (
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    proveedor_actual["codigo"],
                    proveedor_actual["nombre"],
                    subtotal,
                    impuesto,
                    total,
                ),
            )
            
            conn_e.commit()

            id_compra = cur_e.lastrowid

            # 🔵 RECORRER CARRITO
            
            for i in carrito:
                
                # ===========================
                # GUARDAR DETALLE COMPRA
                # ===========================

                cur_e.execute(
                    """
                    INSERT INTO detalle_compra
                    (id_compra, codigo, descripcion, cantidad, costo, subtotal)
                    VALUES (?,?,?,?,?,?)
                    """,
                    (
                        id_compra,
                        i["codigo"],
                        i["descripcion"],
                        i["cantidad"],
                        i["costo"],
                        i["subtotal"],
                    ),
                )

                # =======================
                # actualizar inventario
                # =======================
                
                cur_i.execute(
                    """
                    UPDATE inventario
                    SET cantidad = cantidad + ?,
                    costo = ?
                    WHERE codigo = ?
                    """,
                    (
                        i["cantidad"] * cfg["factor"],
                        i["costo"],
                        i["codigo"]
                    ),
                )
                 
                # -----------------------------------
                # 🟢 REGISTRAR MOVIMIENTO (SIEMPRE)
                # -----------------------------------
            
                registrar_movimiento(
                    producto_id=i["codigo"],
                    tipo=cfg["mov_tipo"],
                    cantidad=i["cantidad"] * cfg["factor"], 
                    referencia=cfg["titulo"],
                )
                
            # ===========================
            # GUARDAR CAMBIOS
            # ===========================
            
            conn_m.commit()
            conn_e.commit()
            conn_i.commit()

            # ===========================
            # CERRAR CONEXIONES
            # ===========================
            
            conn_m.close()
            conn_e.close()
            conn_i.close()
            
            items = []

            for p in carrito:
                items.append(
                    {
                        "codigo": p["codigo"],
                        "producto": p["descripcion"],
                        "cantidad": p["cantidad"],
                        "precio": p["costo"],
                        "total": p["subtotal"],
                    }
                )

            archivo = f"documentos/inventario/entradas/entrada_{id_compra:05d}.pdf"

            crear_documentoc("ENTRADA INVENTARIO", id_compra, proveedor_actual["nombre"], items, archivo,)
            
            messagebox.showinfo("Entrada", f"Entrada #{id_compra} registrada")

        # ================== FIN DE ENTRADA ===================================

        # =====================================================================
        # 🔵 SOLO SI ES SALIDA DE INVENTARIO
        # =====================================================================
        if modo == "SALIDA":

            cur_s.execute(
                """
                INSERT INTO ventas
                (fecha, cliente_codigo, cliente_nombre, subtotal, impuesto, total)
                VALUES (?,?,?,?,?,?)
                """,
                (
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    proveedor_actual["codigo"],
                    proveedor_actual["nombre"],
                    subtotal,
                    impuesto,
                    total,
                ),
            )
            conn_s.commit()

            id_compra = cur_s.lastrowid

            # 🔵 RECORRER CARRITO
            
            for i in carrito:
                
                # =======================================
                # 🟢 SOLO SI ES SALIDA → guardar detalle
                # =======================================
            
                cur_s.execute(
                    """
                    INSERT INTO detalle_venta
                    (id_venta, codigo, descripcion, cantidad, precio, subtotal)
                    VALUES (?,?,?,?,?,?)
                    """,
                    (
                        id_compra,
                        i["codigo"],
                        i["descripcion"],
                        i["cantidad"],
                        i["costo"],
                        i["subtotal"],
                    ),
                )

                # ===========================
                # 🟢 ACTUALIZAR INVENTARIO (SIEMPRE)
                # ===========================            
            
                cur_i.execute(
                    """
                    UPDATE inventario
                    SET cantidad = cantidad - ?,
                    costo = ?
                    WHERE codigo = ?
                    """,
                    (i["cantidad"] * cfg["factor"], i["costo"], i["codigo"]),
                )
         
                # ===========================
                # 🟢 REGISTRAR MOVIMIENTO (SIEMPRE)
                # ===========================
                
                registrar_movimiento(
                    producto_id=i["codigo"],
                    tipo=cfg["mov_tipo"],
                    cantidad=i["cantidad"] * cfg["factor"],
                    referencia=cfg["titulo"],
                )
                
            # ===========================
            # GUARDAR CAMBIOS
            # ===========================
            
            conn_m.commit()
            conn_s.commit()
            conn_i.commit()
            
            # ===========================
            # CERRAR CONEXIONES
            # ===========================            
            
            conn_m.close()
            conn_s.close()
            conn_i.close()
            

            # 🔵 Mensaje diferente según modo

            items = []

            for p in carrito:
                items.append(
                    {
                        "codigo": p["codigo"],
                        "producto": p["descripcion"],
                        "cantidad": p["cantidad"],
                        "precio": p["costo"],
                        "total": p["subtotal"],
                    }
                )

            archivo = f"documentos/inventario/salidas/salida_{id_compra:05d}.pdf"

            crear_documentoc("SALIDA DE INVENTARIO", id_compra, proveedor_actual["nombre"], items, archivo,)
            
            messagebox.showinfo("Salida", f"Salida #{id_compra} registrada")

        limpiar_venta()

    # ================== BOTONES ==================

    btns = ctk.CTkFrame(main)
    btns.pack(fill="x", pady=15)

    btn_cobro = ctk.CTkButton(
        btns,
        text="💰 F2 - COBRAR" if cfg["usa_cobro"] else "✅ F2 - PROCESAR",
        width=240,
        height=60,
        font=("Segoe UI", 18, "bold"),
        command=accion_principal,
    )
    btn_cobro.pack(side="left", padx=10)

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
