from core import *
from models.categorias_model import (
    crear_tabla_categorias,
    listar_categorias,
    agregar_categoria,
    actualizar_categoria,
    eliminar_categoria,
    obtener_categoria,
)

def abrir_categorias(parent):
    
    if hasattr(parent, "cat_abierto") and parent.cat_abierto:
        return
    parent.cat_abierto = True

    crear_tabla_categorias()

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
        main, text="📂 GESTIÓN DE CATEGORÍAS", font=("Segoe UI", 26, "bold")
    ).pack(pady=10)

    # ================= FORM =================
    form = ctk.CTkFrame(main)
    form.pack(fill="x", pady=10)

    entries = {}

    ctk.CTkLabel(form, text="Código").grid(row=0, column=0, sticky="e", padx=6, pady=6)
    entries["codigo"] = ctk.CTkEntry(form)
    entries["codigo"].grid(row=0, column=1, padx=6, pady=6)

    ctk.CTkLabel(form, text="Nombre").grid(row=0, column=2, sticky="e", padx=6, pady=6)
    entries["nombre"] = ctk.CTkEntry(form, width=300)
    entries["nombre"].grid(row=0, column=3, padx=6, pady=6)

    # ================= BUSCAR =================
    top = ctk.CTkFrame(main)
    top.pack(fill="x", pady=10)

    entry_buscar = ctk.CTkEntry(
        top, placeholder_text="Buscar por código o nombre", width=300
    )
    entry_buscar.pack(side="left", padx=10)

    ###########################################################

    btns = ctk.CTkFrame(top)
    btns.pack(side="left", padx=10)

    btn_buscar = ctk.CTkButton(btns, text="🔍 Buscar")
    btn_agregar = ctk.CTkButton(btns, text="➕ Agregar")
    btn_actualizar = ctk.CTkButton(btns, text="✏️ Actualizar")
    btn_eliminar = ctk.CTkButton(btns, text="🗑️ Eliminar")
    btn_limpiar = ctk.CTkButton(btns, text="🧹 Limpiar")
    btn_salir = ctk.CTkButton(btns, text="❌ Salir", width=130,  fg_color="#8B0000", command=cerrar)

    for b in (
        btn_buscar,
        btn_agregar,
        btn_actualizar,
        btn_eliminar,
        btn_limpiar,
        btn_salir,
    ):
        b.pack(side="left", padx=4)

    # ================= TABLA =================
    tree = ttk.Treeview(main, columns=("codigo", "nombre"), show="headings", height=18)

    tree.heading("codigo", text="CÓDIGO")
    tree.heading("nombre", text="NOMBRE")
    tree.column("codigo", anchor="center", width=150)
    tree.column("nombre", anchor="w", width=400)
    tree.pack(fill="x", padx=10, pady=10)

    # ================= REPORTES =================
    frame_reportes = ctk.CTkFrame(main, fg_color="transparent")
    frame_reportes.pack(fill="x", padx=10, pady=(0, 10))

    crear_botones_reporte(frame_reportes, tree, "CATEGORIAS")

    # ================= MODOS =================
    def modo_agregar():
        entries["codigo"].configure(state="normal")
        btn_agregar.configure(state="normal")
        btn_actualizar.configure(state="disabled")
        btn_eliminar.configure(state="disabled")

    def modo_editar():
        entries["codigo"].configure(state="disabled")  # 🔒 CLAVE
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
        modo_agregar()
        
    def listar(filtro=""):
        tree.delete(*tree.get_children())
        for fila in listar_categorias(filtro):
            tree.insert("", "end", values=fila)

    def buscar():
        listar(entry_buscar.get().strip())

    def agregar():
        data = (
            entries["codigo"].get() or 0,
            entries["nombre"].get().strip().upper()
        )
        
        if not data[0] or not data[1]:
            messagebox.showerror("Error", "Código y nombre son obligatorios")
            listar()
            limpiar()
            return
        try:
            guardado = agregar_categoria(data)
            listar()
            limpiar()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        if not guardado:
            return
    
    def actualizar():
        codigo = entries["codigo"].get()
        if not codigo:
            return
        nombre = entries["nombre"].get().strip().upper()
        actualizar_categoria((nombre, int(codigo)))
        listar()
        limpiar()

    def eliminar():
        codigo = entries["codigo"].get()
        if not codigo:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar categoría?"):
            return
        eliminar_categoria(codigo)
        listar()
        limpiar()

    def seleccionar(_):
        item = tree.focus()
        if not item:
            return
        codigo = tree.item(item, "values")[0]
        data = obtener_categoria(codigo)

        entries["codigo"].configure(state="normal")
        entries["codigo"].delete(0, tk.END)
        entries["codigo"].insert(0, data[0])
        entries["codigo"].configure(state="disabled")  # 🔒
        entries["nombre"].delete(0, tk.END)
        entries["nombre"].insert(0, data[1])

        modo_editar()

    # ================= BINDS =================
    btn_buscar.configure(command=buscar)
    btn_agregar.configure(command=agregar)
    btn_actualizar.configure(command=actualizar)
    btn_eliminar.configure(command=eliminar)
    btn_limpiar.configure(command=limpiar)

    tree.bind("<<TreeviewSelect>>", seleccionar)
    
    modo_agregar()
    listar()

