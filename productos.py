import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime
from tkcalendar import DateEntry

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_INV = os.path.join(BASE_DIR, "inventario.db")
DB_PROV = os.path.join(BASE_DIR, "proveedores.db")
DB_CAT = os.path.join(BASE_DIR, "categorias.db")


def abrir_productos(parent):

    if hasattr(parent, "inv_abierto") and parent.inv_abierto:
        return
    parent.inv_abierto = True

    # ================= UTIL =================
    def conectar(db):
        return sqlite3.connect(db)

    # ================= DB =================
    conn = conectar(DB_INV)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventario(
            codigo INTEGER PRIMARY KEY,
            proveedor INTEGER,
            descripcion TEXT,
            cantidad INTEGER,
            costo REAL,
            porcentaje INTEGER,
            impuesto REAL,
            precio_detal REAL,
            precio_mayor REAL,
            categoria INTEGER,
            fecha_compra TEXT
        )
    """)
    conn.commit()
    conn.close()

    def cargar(db, tabla):
        conn = conectar(db)
        cur = conn.cursor()
        cur.execute(f"SELECT codigo, nombre FROM {tabla} ORDER BY nombre")
        datos = cur.fetchall()
        conn.close()
        return datos

    proveedores = cargar(DB_PROV, "proveedores")
    categorias = cargar(DB_CAT, "categorias")

    map_prov = {n: c for c, n in proveedores}
    map_cat = {n: c for c, n in categorias}
    rev_prov = {c: n for c, n in proveedores}
    rev_cat = {c: n for c, n in categorias}

    # ================= VENTANA =================
    win = ctk.CTkToplevel(parent)
    win.title("Productos")
    win.state("zoomed")
    win.transient(parent)
    win.lift()
    win.focus_force()
    win.grab_set()

    def cerrar():
        parent.inv_abierto = False
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", cerrar)

    # ================= CONTENEDOR =================
    main = ctk.CTkFrame(win)
    main.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(
        main,
        text="📦 MÓDULO DE PRODUCTOS",
        font=("Segoe UI", 26, "bold")
    ).pack(pady=(0, 10))

    # ================= FORM =================
    form = ctk.CTkFrame(main)
    form.pack(fill="x", pady=5)

    entries = {}

    def label(txt, r, c):
        ctk.CTkLabel(form, text=txt).grid(row=r, column=c, sticky="e", padx=6, pady=4)

    for i in range(6):
        form.columnconfigure(i, weight=1)

    label("Código", 0, 0)
    entries["codigo"] = ctk.CTkEntry(form)
    entries["codigo"].grid(row=0, column=1, sticky="w")
    entries["codigo"].configure(state="normal")  # ahora desbloqueado al inicio

    label("Proveedor", 0, 2)
    entries["proveedor"] = ctk.CTkComboBox(form, values=list(map_prov.keys()))
    entries["proveedor"].grid(row=0, column=3, sticky="w")

    label("Categoría", 0, 4)
    entries["categoria"] = ctk.CTkComboBox(form, values=list(map_cat.keys()))
    entries["categoria"].grid(row=0, column=5, sticky="w")

    label("Descripción", 1, 0)
    entries["descripcion"] = ctk.CTkEntry(form)
    entries["descripcion"].grid(row=1, column=1, columnspan=5, sticky="we")

    campos_f3 = [
        ("Cantidad", "cantidad"),
        ("Costo", "costo"),
        ("% Utilidad", "porcentaje"),
        ("% Impuesto", "impuesto")
    ]

    for i, (txt, campo) in enumerate(campos_f3):
        label(txt, 2, i * 2)
        entries[campo] = ctk.CTkEntry(form)
        entries[campo].grid(row=2, column=i * 2 + 1, sticky="w")

    label("Precio Detal", 3, 0)
    entries["precio_detal"] = ctk.CTkEntry(form)
    entries["precio_detal"].grid(row=3, column=1, sticky="w")

    label("Precio Mayor", 3, 2)
    entries["precio_mayor"] = ctk.CTkEntry(form)
    entries["precio_mayor"].grid(row=3, column=3, sticky="w")

    label("Fecha Compra", 3, 4)
    date_fecha = DateEntry(
        form,
        width=18,
        date_pattern="dd/mm/yyyy"
    )
    date_fecha.grid(row=3, column=5, sticky="w")
    date_fecha.set_date(datetime.now())

    # ================= BUSCAR =================
    top_bar = ctk.CTkFrame(main)
    top_bar.pack(fill="x", pady=8)

    entry_buscar = ctk.CTkEntry(
        top_bar,
        placeholder_text="Buscar por código o descripción",
        width=300
    )
    entry_buscar.pack(side="left", padx=10)

    btns = ctk.CTkFrame(top_bar)
    btns.pack(side="left", padx=10)

    # ================= TABLA =================
    tabla_frame = ctk.CTkFrame(main)
    tabla_frame.pack(pady=5, fill="x")
    tabla_frame.configure(height=420)
    tabla_frame.pack_propagate(False)

    columnas = [
        "codigo","proveedor","descripcion","cantidad","costo",
        "porcentaje","impuesto","precio_detal","precio_mayor",
        "categoria","fecha_compra"
    ]

    tree = ttk.Treeview(
        tabla_frame,
        columns=columnas,
        show="headings",
        height=18
    )

    for c in columnas:
        tree.heading(c, text=c.upper())
        tree.column(c, anchor="center", width=110)

    tree.pack(fill="x", padx=14, pady=12)

    # ================= LOGICA =================
    precio_detal_editado = False
    precio_mayor_editado = False


    def limpiar():
        nonlocal precio_detal_editado, precio_mayor_editado
        precio_detal_editado = False
        precio_mayor_editado = False

        # desbloquear y limpiar código
        entries["codigo"].configure(state="normal")
        entries["codigo"].delete(0, tk.END)

        for key, e in entries.items():
            if key != "codigo":
                if isinstance(e, ctk.CTkComboBox):
                    e.set("")
                else:
                    e.delete(0, tk.END)

        date_fecha.set_date(datetime.now())
        entry_buscar.delete(0, tk.END)
        tree.selection_remove(tree.selection())


    def recalcular(_=None):
        try:
            costo = float(entries["costo"].get() or 0)
            utilidad = float(entries["porcentaje"].get() or 0)
            impuesto = float(entries["impuesto"].get() or 0)

            base = costo + (costo * impuesto / 100)
            detal = base + (base * utilidad / 100)
            mayor = detal * 0.9

            if not precio_detal_editado:
                entries["precio_detal"].delete(0, tk.END)
                entries["precio_detal"].insert(0, f"{detal:.2f}")

            if not precio_mayor_editado:
                entries["precio_mayor"].delete(0, tk.END)
                entries["precio_mayor"].insert(0, f"{mayor:.2f}")

        except ValueError:
            pass

    def marcar_detal(_):
        nonlocal precio_detal_editado
        precio_detal_editado = True

    def marcar_mayor(_):
        nonlocal precio_mayor_editado
        precio_mayor_editado = True

    entries["precio_detal"].bind("<KeyRelease>", marcar_detal)
    entries["precio_mayor"].bind("<KeyRelease>", marcar_mayor)

    def cambio_base(_):
        nonlocal precio_detal_editado, precio_mayor_editado
        precio_detal_editado = False
        precio_mayor_editado = False
        recalcular()

    for c in ("costo", "porcentaje", "impuesto"):
        entries[c].bind("<KeyRelease>", cambio_base)

    def listar(filtro=""):
        tree.delete(*tree.get_children())
        conn = conectar(DB_INV)
        cur = conn.cursor()

        if filtro:
            cur.execute(
                "SELECT * FROM inventario WHERE codigo LIKE ? OR descripcion LIKE ?",
                (f"%{filtro}%", f"%{filtro}%")
            )
        else:
            cur.execute("SELECT * FROM inventario")

        for f in cur.fetchall():
            f = list(f)
            f[1] = rev_prov.get(f[1], "")
            f[9] = rev_cat.get(f[9], "")
            tree.insert("", "end", values=f)

        conn.close()

    def buscar():
        listar(entry_buscar.get())

    def seleccionar(_):
        nonlocal precio_detal_editado, precio_mayor_editado
        precio_detal_editado = True
        precio_mayor_editado = True

        item = tree.focus()
        if not item:
            return
        v = tree.item(item, "values")

        # ACTUALIZAR CAMPOS
        for i, c in enumerate(columnas):
            if c not in ("proveedor", "categoria", "fecha_compra"):
                if c != "codigo":  # NO EDITAR CÓDIGO DIRECTAMENTE
                    entries[c].delete(0, tk.END)
                    entries[c].insert(0, v[i])

        # BLOQUEAR CÓDIGO
        entries["codigo"].configure(state="normal")
        entries["codigo"].delete(0, tk.END)
        entries["codigo"].insert(0, v[0])
        entries["codigo"].configure(state="disabled")

        entries["proveedor"].set(v[1])
        entries["categoria"].set(v[9])

        if v[10]:
            date_fecha.set_date(datetime.strptime(v[10], "%d/%m/%Y"))

    tree.bind("<<TreeviewSelect>>", seleccionar)

    # ================= CRUD =================
    def agregar():
        try:
            fecha = date_fecha.get()
            conn = conectar(DB_INV)
            cur = conn.cursor()
            cur.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?,?,?,?,?,?)", (
                int(entries["codigo"].get()),
                map_prov[entries["proveedor"].get()],
                entries["descripcion"].get().upper(),
                int(entries["cantidad"].get()),
                float(entries["costo"].get()),
                int(entries["porcentaje"].get()),
                float(entries["impuesto"].get()),
                float(entries["precio_detal"].get()),
                float(entries["precio_mayor"].get()),
                map_cat[entries["categoria"].get()],
                fecha
            ))
            conn.commit()
            conn.close()
            listar()
            limpiar()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def actualizar():
        if not entries["codigo"].get():
            return

        fecha = date_fecha.get()

        conn = conectar(DB_INV)
        cur = conn.cursor()
        cur.execute("""
            UPDATE inventario SET proveedor=?, descripcion=?, cantidad=?, costo=?,
            porcentaje=?, impuesto=?, precio_detal=?, precio_mayor=?, categoria=?, fecha_compra=?
            WHERE codigo=?
        """, (
            map_prov[entries["proveedor"].get()],
            entries["descripcion"].get().upper(),
            int(entries["cantidad"].get()),
            float(entries["costo"].get()),
            int(entries["porcentaje"].get()),
            float(entries["impuesto"].get()),
            float(entries["precio_detal"].get()),
            float(entries["precio_mayor"].get()),
            map_cat[entries["categoria"].get()],
            fecha,
            int(entries["codigo"].get())
        ))
        conn.commit()
        conn.close()
        listar()
        limpiar()

    def eliminar():
        if not entries["codigo"].get():
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar registro?"):
            return
        conn = conectar(DB_INV)
        cur = conn.cursor()
        cur.execute("DELETE FROM inventario WHERE codigo=?", (entries["codigo"].get(),))
        conn.commit()
        conn.close()
        listar()
        limpiar()

    # ================= BOTONES =================
    ctk.CTkButton(btns, text="🔍 Buscar", width=130, command=buscar).pack(side="left", padx=4)
    ctk.CTkButton(btns, text="➕ Agregar", width=130, command=agregar).pack(side="left", padx=4)
    ctk.CTkButton(btns, text="✏️ Actualizar", width=130, command=actualizar).pack(side="left", padx=4)
    ctk.CTkButton(btns, text="🗑️ Eliminar", width=130, command=eliminar).pack(side="left", padx=4)
    ctk.CTkButton(btns, text="🧹 Limpiar", width=130, command=limpiar).pack(side="left", padx=4)

    listar()
