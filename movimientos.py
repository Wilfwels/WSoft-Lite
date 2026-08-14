from core import *
from config import *
import sqlite3
import customtkinter as ctk
from tkinter import ttk
from reportes.factura_venta import factura_venta, factura_salidas
from reportes.factura_compra import factura_compra, factura_compra_en
from reportes.entrada_inventario import factura_entrada
from reportes.salida_inventario import factura_salida
from reportes.factura_compra import factura_compra_id

# from reportes.entrada_inventario import entrada_inventario_id
# from reportes.salida_inventario import salida_inventario_id


def abrir_movimientos(parent):

    win = ctk.CTkToplevel(parent)
    win.title("Movimientos del Sistema")
    win.geometry("950x550")
    win.grab_set()

    # =============================
    # FILTROS
    # =============================

    frame_top = ctk.CTkFrame(win)
    frame_top.pack(fill="x", padx=10, pady=10)

    tipo = ctk.StringVar(value="TODOS")

    combo_tipo = ctk.CTkComboBox(
        frame_top,
        values=["TODOS", "VENTAS", "COMPRAS", "ENTRADAS", "SALIDAS"],
        variable=tipo,
        width=200,
    )
    combo_tipo.pack(side="left", padx=10)

    buscar = ctk.CTkEntry(frame_top, placeholder_text="Buscar...")
    buscar.pack(side="left", padx=10)

    # =============================
    # TABLA
    # =============================

    columnas = ("TIPO", "NUMERO", "FECHA", "NOMBRE", "TOTAL")

    tree = ttk.Treeview(win, columns=columnas, show="headings")
    tree.tag_configure("VENTA", foreground="#2ecc71")
    tree.tag_configure("COMPRA", foreground="#3498db")
    tree.tag_configure("ENTRADA", foreground="#f39c12")
    tree.tag_configure("SALIDA", foreground="#e74c3c")

    for c in columnas:
        tree.heading(c, text=c)
        tree.column(c, anchor="center")

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # =============================
    # FUNCION CARGAR
    # =============================

    def cargar():

        for i in tree.get_children():
            tree.delete(i)

        conn = sqlite3.connect(DB_VENTAS)
        cur = conn.cursor()

        conn_c = sqlite3.connect(DB_COMPRAS)
        cur_c = conn_c.cursor()

        conn_e = sqlite3.connect(DB_ENTRADAS)
        cur_e = conn_e.cursor()

        conn_s = sqlite3.connect(DB_SALIDAS)
        cur_s = conn_s.cursor()

        t = tipo.get()

        movimientos = []

        if t in ("TODOS", "VENTAS"):

            cur.execute("""
                SELECT 'VENTA', id, fecha, cliente_nombre, total
                FROM ventas
            """)

            movimientos += cur.fetchall()

        if t in ("TODOS", "COMPRAS"):

            cur_c.execute("""
                SELECT 'COMPRA', id, fecha, proveedor_nombre, total
                FROM compras
            """)

            movimientos += cur_c.fetchall()

        if t in ("TODOS", "ENTRADAS"):

            cur_e.execute("""
                SELECT 'ENTRADA', id, fecha, proveedor_nombre, total
                FROM compras
            """)

            movimientos += cur_e.fetchall()

        if t in ("TODOS", "SALIDAS"):

            cur_s.execute("""
                SELECT 'SALIDA', id, fecha, cliente_nombre, total
                FROM ventas
            """)

            movimientos += cur_s.fetchall()

        conn.close()
        conn_c.close()
        conn_e.close()
        conn_s.close()

        movimientos.sort(key=lambda x: x[2], reverse=True)

        texto = buscar.get().lower()

        for m in movimientos:

            if texto:
                if texto not in str(m).lower():
                    continue

            tree.insert("", "end", values=m, tags=(m[0],))

    combo_tipo.configure(command=lambda e: cargar())
    buscar.bind("<KeyRelease>", lambda e: cargar())

    # =============================
    # REIMPRIMIR DOCUMENTO
    # =============================

    def reimprimir():

        sel = tree.selection()

        if not sel:
            return

        datos = tree.item(sel)["values"]
        
        #print(datos)   # <-- Agrega est

        tipo_doc = datos[0]
        numero = datos[1]
        
        if tipo_doc == "VENTA":

            archivo = factura_venta(numero)

            if archivo and os.path.exists(archivo):
                os.startfile(archivo)


        elif tipo_doc == "COMPRA":
            archivo = factura_compra_id(numero)

            if archivo and os.path.exists(archivo):
                os.startfile(archivo)

        elif tipo_doc == "ENTRADA":
            archivo = factura_compra_en(numero)

            if archivo and os.path.exists(archivo):
                os.startfile(archivo)
            
        elif tipo_doc == "SALIDA":

            archivo = factura_salidas(numero)

            if archivo and os.path.exists(archivo):
                os.startfile(archivo)

    # =============================
    # BOTONES
    # =============================

    frame_btn = ctk.CTkFrame(win)
    frame_btn.pack(pady=10)

    btn_reimprimir = ctk.CTkButton(
        frame_btn, text="Reimprimir Documento", command=reimprimir
    )
    btn_reimprimir.pack(side="left", padx=10)

    # =============================
    # DOBLE CLICK
    # =============================

    tree.bind("<Double-1>", lambda e: reimprimir())

    cargar()
