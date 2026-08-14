from config import *
from core import *
from models.vendedores_model import (
    crear_tabla_vendedores,
    listar_vendedores,
    agregar_vendedor,
    actualizar_vendedor,
    eliminar_vendedor,
    obtener_vendedor,
)

def abrir_vendedores(parent, modo="admin", callback=None):
    

    if hasattr(parent, "cat_abierto") and parent.cat_abierto:
        return
    parent.cat_abierto = True

    crear_tabla_vendedores()

    win = ctk.CTkToplevel(parent)
    win.title("Categorías")
    win.state("zoomed")
    win.transient(parent)
    win.grab_set()

    def cerrar():
        parent.cat_abierto = False
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", cerrar)

    main = ctk.CTkFrame(win)
    main.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(
        main, text="📂 GESTIÓN DE VENDEDORES", font=("Segoe UI", 26, "bold")
    ).pack(pady=10)

    # ================= FORM =================
    form = ctk.CTkFrame(main)
    form.pack(fill="x", pady=10)

    campos = [
        ("codigo", "Código"),
        ("nombre", "Nombre"),
        ("contacto","Contacto"),
        ("telefono", "Teléfono"),
        ("correo", "Correo"),
        ("direccion", "Dirección"),
        ("ciudad", "Ciudad"),
    ]

    entries = {}
    for i in range(6):
        form.columnconfigure(i, weight=1)

    for i, (key, label_txt) in enumerate(campos):
        ctk.CTkLabel(form, text=label_txt).grid(
            row=i // 3, column=(i % 3) * 2, sticky="e", padx=6, pady=6
        )
        e = ctk.CTkEntry(form, width=220)
        e.grid(row=i // 3, column=(i % 3) * 2 + 1, sticky="w", padx=6, pady=6)
        entries[key] = e

    # ================= BUSCAR + BOTONES =================
    top = ctk.CTkFrame(main)
    top.pack(fill="x", pady=10)

    entry_buscar = ctk.CTkEntry(
        top, placeholder_text="Buscar por código o nombre", width=320
    )
    entry_buscar.pack(side="left", padx=10)

    btns = ctk.CTkFrame(top)
    btns.pack(side="left", padx=10)

    btn_agregar = ctk.CTkButton(btns, text="➕ Agregar")
    btn_actualizar = ctk.CTkButton(btns, text="✏️ Actualizar")
    btn_eliminar = ctk.CTkButton(btns, text="🗑️ Eliminar")
    btn_limpiar = ctk.CTkButton(btns, text="🧹 Limpiar")
    btn_salir = ctk.CTkButton(btns, text="❌ Salir", width=130,  fg_color="#8B0000", command=cerrar)
    
    btn_agregar.pack(side="left", padx=4)
    btn_actualizar.pack(side="left", padx=4)
    btn_eliminar.pack(side="left", padx=4)
    btn_limpiar.pack(side="left", padx=4)
    btn_salir.pack(side="left", padx=4 )

    # ================= TABLA =================
    tabla_frame = ctk.CTkFrame(main)
    tabla_frame.pack(fill="x", pady=10)

    columnas = ("codigo", "nombre", "contacto", "telefono", "correo", "direccion", "ciudad")
    tree = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=18)
    for col in columnas:
        tree.heading(col, text=col.upper())
        tree.column(col, width=150)
    tree.pack(fill="x", padx=10, pady=10)

    # ================= REPORTES =================
    frame_reportes = ctk.CTkFrame(main, fg_color="transparent")
    frame_reportes.pack(fill="x", padx=10, pady=(0, 10))

    crear_botones_reporte(frame_reportes, tree, "VENDEDORES")

    # ================= FUNCIONES =================
    def datos_form():
        return [entries[c].get().strip().upper() for c, _ in campos]

    def limpiar():
        entries["codigo"].configure(state="normal")
        entries["codigo"].delete(0, tk.END)
        for key, e in entries.items():
            if key != "codigo":
                e.configure(state="normal")
                e.delete(0, tk.END)
        entry_buscar.delete(0, tk.END)
        tree.selection_remove(tree.selection())

        # Botones: activar agregar, desactivar actualizar/eliminar
        btn_agregar.configure(state="normal")
        btn_actualizar.configure(state="disabled")
        btn_eliminar.configure(state="disabled")

    def listar(filtro=""):
        tree.delete(*tree.get_children())
        for fila in listar_vendedores(filtro):
            tree.insert("", "end", values=fila)
            
    def buscar():
        listar(entry_buscar.get().strip())

    def agregar():
        data = (
            entries["codigo"].get() or 0,
            entries["nombre"].get().strip().upper(),
            entries["contacto"].get().upper(),
            entries["telefono"].get().upper(),
            entries["correo"].get().upper(),
            entries["direccion"].get().upper(),
            entries["ciudad"].get().upper()
        )
        
        if not data[0] or not data[1]:
            messagebox.showerror("Error", "Código y nombre son obligatorios")
            listar()
            limpiar()
            return
        try:
            guardado = agregar_vendedor(data)
            listar()
            limpiar()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        
        if not guardado:
            return        
        listar()
        limpiar()
        
    def actualizar():
        codigo = entries["codigo"].get().strip()
        if not codigo:
            return
        data = (
            entries["nombre"].get().upper(),
            entries["contacto"].get().upper(),
            entries["telefono"].get().upper(),
            entries["correo"].get().upper(),
            entries["direccion"].get().upper(),
            entries["ciudad"].get().upper(),
            codigo,
        )
        actualizar_vendedor(data)
        listar()
        limpiar()
        

    def eliminar():
        codigo = entries["codigo"].get().strip()
        if not codigo:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar Vendedor?"):
            return
        eliminar_vendedor(codigo)
        listar()
        limpiar()   
        
        item = tree.focus()
        if not item:
            return
        codigo = tree.item(item, "values")[0]

    def seleccionar(_=None):
        item = tree.focus()
        if not item:
            return
        
        data = obtener_vendedor(tree.item(item, "values")[0])

        if modo == "seleccion" and callback:
            callback(data[0], data[1])  # codigo, nombre
            cerrar()
            return
        
        codigo = tree.item(item, "values")[0]
        data = obtener_vendedor(codigo)
        
        entries["codigo"].insert(0, str(data[0] or ""))
        entries["nombre"].insert(0, str(data[1] or ""))
        entries["contacto"].insert(0, str(data[2] or ""))
        entries["telefono"].insert(0, str(data[3] or ""))
        entries["correo"].insert(0, str(data[4] or ""))
        entries["direccion"].insert(0, str(data[5] or ""))
        entries["ciudad"].insert(0, str(data[6] or ""))
    
        # Botones: desactivar agregar, activar actualizar/eliminar
        btn_agregar.configure(state="disabled")
        btn_actualizar.configure(state="normal")
        btn_eliminar.configure(state="normal")

    tree.bind("<<TreeviewSelect>>", seleccionar)


    # ================= ASIGNAR BOTONES =================
    btn_agregar.configure(command=agregar)
    btn_actualizar.configure(command=actualizar)
    btn_eliminar.configure(command=eliminar)
    btn_limpiar.configure(command=limpiar)

    # Inicial: activar agregar, desactivar actualizar/eliminar
    btn_agregar.configure(state="normal")
    btn_actualizar.configure(state="disabled")
    btn_eliminar.configure(state="disabled")

    limpiar()
    listar()
