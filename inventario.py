from core import *
from config import *
from models.inventario_model import (
    crear_tabla_inventario,
    listar_inventario,
    agregar_producto,
    actualizar_producto,
    eliminar_producto,
    cargar_proveedores,
    cargar_categorias,
)
import config


def es_admin(usuario):
    return usuario["rol"] == "ADMIN"


def abrir_inventario(parent, modo="normal", callback=None):
    
    
    if hasattr(parent, "inv_abierto") and parent.inv_abierto:
        return
    parent.inv_abierto = True

    crear_tabla_inventario()

    proveedores = cargar_proveedores()
    categorias = cargar_categorias()

    map_prov = {n: c for c, n in proveedores}
    map_cat = {n: c for c, n in categorias}
    rev_prov = {c: n for c, n in proveedores}
    rev_cat = {c: n for c, n in categorias}

    # ================= VENTANA =================
    win = ctk.CTkToplevel(parent)
    win.title("Inventario")
    win.state("zoomed")
    win.transient(parent)
    win.grab_set()

    def salir():
        parent.inv_abierto = False
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", salir)

    main = ctk.CTkFrame(win)
    main.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(
        main, text="📦 MÓDULO DE INVENTARIO 📦", font=("Segoe UI", 26, "bold")
    ).pack(pady=10)

    # ================= FORM =================
    form = ctk.CTkFrame(main)
    form.pack(fill="x")

    entries = {}
    precio_editado = False
    bloqueando = False

    def label(txt, r, c):
        ctk.CTkLabel(form, text=txt).grid(row=r, column=c, sticky="e", padx=6, pady=4)

    for i in range(6):
        form.columnconfigure(i, weight=1)

    label("Código", 0, 0)
    entries["codigo"] = ctk.CTkEntry(form)
    entries["codigo"].grid(row=0, column=1)

    label("Proveedor", 0, 2)
    entries["proveedor"] = ctk.CTkComboBox(form, values=list(map_prov.keys()))
    entries["proveedor"].grid(row=0, column=3)

    label("Categoría", 0, 4)
    entries["categoria"] = ctk.CTkComboBox(form, values=list(map_cat.keys()))
    entries["categoria"].grid(row=0, column=5)

    label("Descripción", 1, 0)
    entries["descripcion"] = ctk.CTkEntry(form)
    entries["descripcion"].grid(row=1, column=1, columnspan=5, sticky="we")

    campos = [
        ("Cantidad", "cantidad"),
        ("Costo", "costo"),
        ("% Utilidad", "porcentaje"),
        ("% Impuesto", "impuesto"),
    ]

    for i, (txt, campo) in enumerate(campos):
        label(txt, 2, i * 2)
        entries[campo] = ctk.CTkEntry(form)
        entries[campo].grid(row=2, column=i * 2 + 1)

    label("Precio Detal", 3, 0)
    entries["precio_detal"] = ctk.CTkEntry(form)
    entries["precio_detal"].grid(row=3, column=1)

    label("Precio Mayor", 3, 2)
    entries["precio_mayor"] = ctk.CTkEntry(form)
    entries["precio_mayor"].grid(row=3, column=3)

    label("Fecha Compra", 3, 4)
    fecha = DateEntry(form, date_pattern="dd/mm/yyyy")
    fecha.grid(row=3, column=5)
    fecha.set_date(datetime.now())

    label("Stock Minimo", 3, 6)
    entries["stock_minimo"] = ctk.CTkEntry(form)
    entries["stock_minimo"].grid(row=3, column=7)

    # ================= CALCULO DE PRECIOS =================
    def calcular_precios():
        nonlocal precio_editado
        if precio_editado:
            return

        try:
            costo = float(entries["costo"].get())
            utilidad = float(entries["porcentaje"].get())
            impuesto = float(entries["impuesto"].get())

            precio_mayor = round(costo + (costo * utilidad / 100), 2)
            precio_detal = round(precio_mayor + (precio_mayor * impuesto / 100), 2)

            entries["precio_mayor"].delete(0, tk.END)
            entries["precio_mayor"].insert(0, f"{precio_mayor:.2f}")

            entries["precio_detal"].delete(0, tk.END)
            entries["precio_detal"].insert(0, f"{precio_detal:.2f}")
        except:
            pass

    def marcar_editado(_):
        nonlocal precio_editado
        precio_editado = True

    def recalcular(_):
        nonlocal precio_editado
        precio_editado = False
        calcular_precios()

    for c in ("costo", "porcentaje", "impuesto"):
        entries[c].bind("<KeyRelease>", recalcular)

    entries["precio_detal"].bind("<KeyRelease>", marcar_editado)
    entries["precio_mayor"].bind("<KeyRelease>", marcar_editado)

    # ================= BUSCAR =================
    top = ctk.CTkFrame(main)
    top.pack(fill="x", pady=10)

    entry_buscar = ctk.CTkEntry(top, width=400, placeholder_text="Codigo o Abreviaura para Buscar")
    entry_buscar.pack(side="left", padx=10)

    def buscar():
        listar(entry_buscar.get())

    ctk.CTkButton(top, text="Buscar", command=buscar).pack(side="left")

    # ================= TABLA =================
    columnas = [
        "codigo",
        "proveedor",
        "descripcion",
        "cantidad",
        "costo",
        "porcentaje",
        "impuesto",
        "precio_detal",
        "precio_mayor",
        "categoria",
        "fecha_compra",
        "stock_minimo",
    ]

    tree = ttk.Treeview(main, columns=columnas, show="headings", height=16)
    for c in columnas:
        tree.heading(c, text=c.upper())
        tree.column(c, anchor="center", width=110)
    tree.pack(fill="x", padx=10)

    # ================= ESTADOS =================
    def estado_nuevo():
        btn_agregar.configure(state="normal")
        btn_actualizar.configure(state="disabled")
        btn_eliminar.configure(state="disabled")

    def estado_edicion():
        btn_agregar.configure(state="disabled")
        btn_actualizar.configure(state="normal")
        btn_eliminar.configure(state="normal")

    # ================= FUNCIONES =================
        
    def limpiar():
        nonlocal precio_editado, bloqueando

        bloqueando = True

        for e in entries.values():
            if isinstance(e, ctk.CTkComboBox):
                e.set("")
            else:
                e.delete(0, tk.END)

        fecha.set_date(datetime.now())
        tree.selection_remove(tree.selection())
        precio_editado = False
        estado_nuevo()

        def liberar():
            nonlocal bloqueando
            bloqueando = False

        win.after(50, liberar)
            
    def listar(filtro=""):

        if not tree.winfo_exists():
            return

        tree.delete(*tree.get_children())

        for f in listar_inventario(filtro):
            tree.insert("", "end", values=list(f))

    """def listar(filtro=""):
        tree.delete(*tree.get_children())
        for f in listar_inventario(filtro):
            f = list(f)
           # f[1] = rev_prov.get(f[1], "")
           # f[9] = rev_cat.get(f[9], "")
            tree.insert("", "end", values=f)"""

    def seleccionar(_):
        nonlocal precio_editado
        if bloqueando:
            return

        item = tree.focus()
        if not item:
            return

        v = tree.item(item, "values")

        precio_editado = True  # 👈 CLAVE: NO RECALCULAR AL SELECCIONAR

        for i, c in enumerate(columnas):
            if c in ("proveedor", "categoria", "fecha_compra"):
                continue
            entries[c].delete(0, tk.END)
            entries[c].insert(0, v[i])

        entries["proveedor"].set(v[1])
        entries["categoria"].set(v[9])
        fecha.set_date(datetime.strptime(v[10], "%d/%m/%Y"))

        estado_edicion()

    tree.bind("<<TreeviewSelect>>", seleccionar)

    # ================= CRUD =================
    def agregar():
        calcular_precios()
        data = (
            int(entries["codigo"].get()),
            map_prov[entries["proveedor"].get()],
            entries["descripcion"].get().upper(),
            float(entries["cantidad"].get() or 0),
            float(entries["costo"].get() or 0),
            int(entries["porcentaje"].get() or 0),
            float(entries["impuesto"].get() or 0),
            float(entries["precio_detal"].get() or 0),
            float(entries["precio_mayor"].get() or 0),
            map_cat[entries["categoria"].get()],
            fecha.get(),
            int(entries["stock_minimo"].get() or 0),
        )

        guardado = agregar_producto(data)
        
        listar()
        limpiar()
        
        if not guardado:
            return
    
    def actualizar():
        categoria = entries["categoria"].get()
        categoria_id = map_cat.get(categoria)
        if categoria_id is None:
            messagebox.showwarning(
                "Categoría",
                "Seleccione una categoría válida"
            )

            return
        
        proveedor = entries["proveedor"].get()
        proveedor_id = map_prov.get(proveedor)
        if proveedor_id is None:
            messagebox.showwarning(
                "Proveedor",
                "Seleccione una proveedor válida"
            )

            return
        calcular_precios()
        data = (
            map_prov[entries["proveedor"].get()],
            entries["descripcion"].get().upper(),
            float(entries["cantidad"].get() or 0),
            float(entries["costo"].get() or 0),
            float(entries["porcentaje"].get() or 0),
            float(entries["impuesto"].get() or 0),
            float(entries["precio_detal"].get() or 0),
            float(entries["precio_mayor"].get() or 0),
            map_cat[entries["categoria"].get()],
            fecha.get(),
            float(entries["stock_minimo"].get() or 0),        
            int(entries["codigo"].get() or 0)
        )
        actualizar_producto(data)
        listar()
        limpiar()

    def eliminar():
        if not messagebox.askyesno("Confirmar", "¿Eliminar producto?"):
            return
        eliminar_producto(int(entries["codigo"].get()))
        listar()
        limpiar()

    # ================= ACCIONES Y REPORTES =================
    acciones_reportes = ctk.CTkFrame(main, fg_color="transparent")
    acciones_reportes.pack(fill="x", padx=10, pady=10)

    frame_reportes = ctk.CTkFrame(acciones_reportes, fg_color="transparent")
    frame_reportes.pack(side="left", padx=(0, 20))

    crear_botones_reporte(frame_reportes, tree, "INVENTARIO")

    botones = ctk.CTkFrame(acciones_reportes, fg_color="transparent")
    botones.pack(side="left")

    btn_agregar = ctk.CTkButton(botones, text="Agregar", command=agregar)
    btn_actualizar = ctk.CTkButton(botones, text="Actualizar", command=actualizar)
    btn_eliminar = ctk.CTkButton(botones, text="Eliminar", command=eliminar)
    btn_limpiar = ctk.CTkButton(botones, text="Limpiar", command=limpiar)
    btn_salir = ctk.CTkButton(botones, text="Salir", fg_color="#8B0000", command=salir)

    if not config.es_admin():
        btn_agregar.configure(state="disabled", text="🔒 Agregar")
        btn_eliminar.configure(state="disabled", text="🔒 Eliminar")

    for b in (btn_agregar, btn_actualizar, btn_eliminar, btn_limpiar, btn_salir):
        b.pack(side="left", padx=6)
        
    listar()
