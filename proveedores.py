from core import *
from models.proveedores_model import (
    crear_tabla_proveedores,
    listar_proveedores,
    obtener_proveedor,
    agregar_proveedor,
    actualizar_proveedor,
    eliminar_proveedor,
)

def abrir_proveedores(parent, modo="admin", callback=None):
    """
    modo = "admin"      -> gestión completa desde menú
    modo = "seleccion"  -> llamado desde Compras, retorna proveedor
    callback(codigo, nombre)
    """

    if hasattr(parent, "prov_abierto") and parent.prov_abierto:
        return
    parent.prov_abierto = True

    crear_tabla_proveedores()

    win = ctk.CTkToplevel(parent)
    win.title("Proveedores")
    win.state("zoomed")
    win.transient(parent)
    win.grab_set()

    def cerrar():
        parent.prov_abierto = False
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", cerrar)

    # ================= CONTENEDOR =================
    main = ctk.CTkFrame(win)
    main.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(
        main, text="🏢 GESTIÓN DE PROVEEDORES", font=("Segoe UI", 26, "bold")
    ).pack(pady=10)

    # ================= FORMULARIO =================
    form = ctk.CTkFrame(main)
    form.pack(fill="x", pady=10)

    entries = {}
    campos = [
        ("codigo", "Código"),
        ("nombre", "Nombre"),
        ("contacto", "Contacto"),
        ("telefono", "Teléfono"),
        ("registro", "Registro"),
        ("direccion", "Dirección"),
        ("ciudad", "Ciudad"),
    ]

    for i, (k, txt) in enumerate(campos):
        r = i // 4
        c = (i % 4) * 4
        ctk.CTkLabel(form, text=txt).grid(row=r, column=c, padx=12, pady=12, sticky="e")
        e = ctk.CTkEntry(form)
        e.grid(row=r, column=c + 1, padx=12, pady=12, sticky="we")
        entries[k] = e

    # ================= BARRA SUPERIOR =================
    top = ctk.CTkFrame(main)
    top.pack(fill="x", pady=10)

    entry_buscar = ctk.CTkEntry(
        top, placeholder_text="Buscar por código o nombre", width=300
    )
    entry_buscar.pack(side="left", padx=6)

    # ================= TABLA =================
    columnas = ("codigo", "nombre", "telefono", "ciudad")
    tree = ttk.Treeview(main, columns=columnas, show="headings", height=18)
    for c in columnas:
        tree.heading(c, text=c.upper())
        tree.column(c, anchor="center", width=140)
    tree.pack(fill="x", padx=10, pady=10)

    # ================= REPORTES =================
    frame_reportes = ctk.CTkFrame(main, fg_color="transparent")
    frame_reportes.pack(fill="x", padx=10, pady=(0, 10))

    crear_botones_reporte(frame_reportes, tree, "PROVEEDORES")

    # ================= ESTADOS =================
    def estado_agregar():
        btn_agregar.configure(state="normal")
        btn_actualizar.configure(state="disabled")
        btn_eliminar.configure(state="disabled")

    def estado_editar():
        btn_agregar.configure(state="disabled")
        btn_actualizar.configure(state="normal")
        btn_eliminar.configure(state="normal")

    # ================= FUNCIONES =================
    def limpiar():
        for e in entries.values():
            e.configure(state="normal")
            e.delete(0, tk.END)
        tree.selection_remove(tree.selection())
        modo_agregar()

    def listar(filtro=""):
        tree.delete(*tree.get_children())
        for fila in listar_proveedores(filtro):
            tree.insert("", "end", values=fila)

    def buscar():
        listar(entry_buscar.get().strip())
          
    def agregar():
    
        data = (
            entries["codigo"].get() or 0,
            entries["nombre"].get().strip().upper(),
            entries["contacto"].get().strip().upper(),
            entries["telefono"].get().strip(),
            entries["registro"].get().strip(),
            entries["direccion"].get().strip().upper(),
            entries["ciudad"].get().strip().upper(),
        )
        
        if not data[0] or not data[1]:
            messagebox.showerror("Error", "Código y nombre son obligatorios")
            listar()
            limpiar()
            return
        try:
            guardado = agregar_proveedor(data)
            listar()
            limpiar()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        if not guardado:
            return

    def actualizar():
        codigo = entries["codigo"].get().strip()
        if not codigo:
            return
        data = (
            entries["nombre"].get().upper(),
            entries["contacto"].get().upper(),
            entries["telefono"].get().upper(),
            entries["registro"].get().upper(),
            entries["direccion"].get().upper(),
            entries["ciudad"].get().upper(),
            codigo,
        )
        actualizar_proveedor(data)
        listar()
        limpiar()

    def eliminar():
        codigo = entries["codigo"].get().strip()
        if not codigo:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar proveedor?"):
            return
        eliminar_proveedor(codigo)
        listar()
        limpiar()

    def seleccionar(_=None):
        item = tree.focus()
        if not item:
            return

        data = obtener_proveedor(tree.item(item, "values")[0])

        if modo == "seleccion" and callback:
            callback(data[0], data[1])  # codigo, nombre
            cerrar()
            return

        # ===== MODO SELECCION (F3 desde compras) =====
        if modo == "seleccion" and callback:
            callback({"codigo": data[0], "nombre": data[1]})
            cerrar()
            return

        # ===== MODO NORMAL (editar proveedor) =====
        for i, k in enumerate(entries):
            entries[k].configure(state="normal")
            entries[k].delete(0, tk.END)
            entries[k].insert(0, str(data[i] or ""))
            if k == "codigo":
                entries[k].configure(state="disabled")

        estado_editar()

    tree.bind("<Double-Button-1>", seleccionar)
    tree.bind("<<TreeviewSelect>>", seleccionar)

    # ================= BOTONES =================
    btn_buscar = ctk.CTkButton(top, text="🔍 Buscar", width=130, command=buscar)
    btn_buscar.pack(side="left", padx=4)

    btn_agregar = ctk.CTkButton(top, text="➕ Agregar", width=130, command=agregar)
    btn_agregar.pack(side="left", padx=4)

    btn_actualizar = ctk.CTkButton(
        top, text="✏️ Actualizar", width=130, command=actualizar
    )
    btn_actualizar.pack(side="left", padx=4)

    btn_eliminar = ctk.CTkButton(top, text="🗑️ Eliminar", width=130, command=eliminar)
    btn_eliminar.pack(side="left", padx=4)

    btn_limpiar = ctk.CTkButton(top, text="🧹 Limpiar", width=130, command=limpiar)
    btn_limpiar.pack(side="left", padx=4)

    # ================= MODOS =================
    def modo_agregar():
        btn_agregar.configure(state="normal")
        btn_actualizar.configure(state="disabled")
        btn_eliminar.configure(state="disabled")
        entries["codigo"].configure(state="normal")

    def modo_editar():
        btn_agregar.configure(state="disabled")
        btn_actualizar.configure(state="normal")
        btn_eliminar.configure(state="normal")

    # ================= INICIO =================
    modo_agregar()
    listar()
