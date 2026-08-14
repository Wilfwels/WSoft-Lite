from core import *
from models.clientes_model import (
    crear_tabla_clientes,
    listar_clientes,
    obtener_cliente,
    agregar_cliente,
    actualizar_cliente,
    eliminar_cliente,
)

def abrir_clientes(parent, modo="admin", callback=None):
    """
    modo = "admin"      -> gestión completa desde menú
    modo = "seleccion"  -> llamado desde Ventas, retorna cliente
    callback(codigo, nombre)
    """

    if hasattr(parent, "cli_abierto") and parent.cli_abierto:
        return
    parent.cli_abierto = True

    crear_tabla_clientes()

    win = ctk.CTkToplevel(parent)
    win.title("Clientes")
    win.state("zoomed")
    win.transient(parent)
    win.grab_set()

    def cerrar():
        parent.cli_abierto = False
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", cerrar)

    main = ctk.CTkFrame(win)
    main.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(
        main,
        text="👥 GESTIÓN DE CLIENTES" if modo == "admin" else "👥 SELECCIONAR CLIENTE",
        font=("Segoe UI", 26, "bold"),
    ).pack(pady=(0, 15))

    # ================= FORM =================
    form = ctk.CTkFrame(main)
    form.pack(fill="x", padx=10, pady=10)

    entries = {}
    campos = [
        ("codigo", "Código"),
        ("nombre", "Nombre"),
        ("contacto", "Contacto"),
        ("telefono", "Teléfono"),
        ("correo", "Correo"),
        ("direccion", "Dirección"),
        ("ciudad", "Ciudad"),
    ]

    for i, (key, txt) in enumerate(campos):
        r = i // 3
        c = (i % 3) * 2
        ctk.CTkLabel(form, text=txt).grid(row=r, column=c, sticky="e", padx=6, pady=6)
        e = ctk.CTkEntry(form)
        e.grid(row=r, column=c + 1, sticky="we", padx=6, pady=6)
        entries[key] = e

    # ================= BUSCAR + BOTONES =================
    top = ctk.CTkFrame(main)
    top.pack(fill="x", pady=10)

    entry_buscar = ctk.CTkEntry(
        top, placeholder_text="Buscar por código o nombre", width=300
    )
    entry_buscar.pack(side="left", padx=10)

    btns = ctk.CTkFrame(top)
    btns.pack(side="left", padx=10)

    # ================= TABLA =================
    tabla_frame = ctk.CTkFrame(main)
    tabla_frame.pack(fill="x", pady=10)

    columnas = ("codigo", "nombre", "telefono", "ciudad")
    tree = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=16)
    for col in columnas:
        tree.heading(col, text=col.upper())
    tree.pack(fill="x", padx=12, pady=12)

    # ================= REPORTES =================
    frame_reportes = ctk.CTkFrame(main, fg_color="transparent")
    frame_reportes.pack(fill="x", padx=10, pady=(0, 10))

    crear_botones_reporte(frame_reportes, tree, "CLIENTES")

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
        entry_buscar.delete(0, tk.END)
        tree.selection_remove(tree.selection())
        estado_agregar()

    def listar(filtro=""):
        tree.delete(*tree.get_children())
        for fila in listar_clientes(filtro):
            tree.insert("", "end", values=fila)

    def buscar():
        listar(entry_buscar.get().strip())

    def agregar():
        datos = {
            k: e.get().strip().upper() if k != "codigo" else e.get().strip()
            for k, e in entries.items()
        }

        if not datos["codigo"] or not datos["nombre"]:
            messagebox.showerror("Error", "Código y nombre obligatorios")
            return

        try:
            agregar_cliente(datos)
            listar()
            limpiar()

            if modo == "seleccion" and callback:
                callback(datos["codigo"], datos["nombre"])
                cerrar()

        except:
            messagebox.showerror("Error", "Código duplicado")
            listar()
            limpiar()

    def actualizar():
        datos = {
            k: e.get().strip().upper() if k != "codigo" else e.get().strip()
            for k, e in entries.items()
        }
        actualizar_cliente(datos)
        listar()
        limpiar()

    def eliminar():
        codigo = entries["codigo"].get()
        if not codigo or not messagebox.askyesno("Confirmar", "¿Eliminar cliente?"):
            return
        eliminar_cliente(codigo)
        listar()
        limpiar()

    def seleccionar(_=None):
        item = tree.focus()
        if not item:
            return

        data = obtener_cliente(tree.item(item, "values")[0])

        if modo == "seleccion" and callback:
            callback(data[0], data[1])  # codigo, nombre
            cerrar()
            return

        for i, k in enumerate(entries):
            entries[k].configure(state="normal")
            entries[k].delete(0, tk.END)
            entries[k].insert(0, data[i])
            if k == "codigo":
                entries[k].configure(state="disabled")

        estado_editar()

    tree.bind("<Double-Button-1>", seleccionar)
    tree.bind("<<TreeviewSelect>>", seleccionar)

    # ================= BOTONES =================
    btn_buscar = ctk.CTkButton(btns, text="🔍 Buscar", width=130, command=buscar)
    btn_agregar = ctk.CTkButton(
        btns,
        text="➕ Crear y usar" if modo == "seleccion" else "➕ Agregar",
        width=130,
        command=agregar,
    )
    btn_actualizar = ctk.CTkButton(
        btns, text="✏️ Actualizar", width=130, command=actualizar
    )
    btn_eliminar = ctk.CTkButton(btns, text="🗑️ Eliminar", width=130, command=eliminar)
    btn_limpiar = ctk.CTkButton(btns, text="🧹 Limpiar", width=130, command=limpiar)
    btn_salir = ctk.CTkButton(btns, text="❌ Salir", width=130,  fg_color="#8B0000", command=cerrar)

    for b in (btn_buscar, btn_agregar, btn_actualizar, btn_eliminar, btn_limpiar, btn_salir):
        b.pack(side="left", padx=4)

    estado_agregar()
    listar()
