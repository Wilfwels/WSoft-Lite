from core import *
from config import *
from models.inventario_model import obtener_faltantes
from utils.barra_reportes import barra_reportes
from utils.centrar_ventana import centrar_ventana


def abrir_reporte_faltantes(parent):

    win = ctk.CTkToplevel(parent)
    win.title("Reporte de Productos Faltantes")
    win.geometry("700x350")
    centrar_ventana(win, 700, 350)
    win.grab_set()

    # ===== TITULO =====
    ctk.CTkLabel(
        win, text="PRODUCTOS POR DEBAJO DEL STOCK MÍNIMO", font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    # ===== TREEVIEW =====
    frame_tree = ctk.CTkFrame(win)
    frame_tree.pack(fill="both", expand=True, padx=10, pady=5)

    tree = ttk.Treeview(
        frame_tree, columns=("codigo", "producto", "stock", "minimo"), show="headings"
    )

    tree.heading("codigo", text="Código")
    tree.heading("producto", text="Producto")
    tree.heading("stock", text="Stock")
    tree.heading("minimo", text="Stock Mínimo")

    tree.column("codigo", width=80, anchor="center")
    tree.column("producto", width=350)
    tree.column("stock", width=80, anchor="center")
    tree.column("minimo", width=100, anchor="center")

    tree.pack(fill="both", expand=True)

    # ===== COLORES =====
    tree.tag_configure("rojo", background="#ffb3b3")
    tree.tag_configure("amarillo", background="#fff3b0")

    # ===== CARGAR DATOS =====
    datos = obtener_faltantes()

    for d in datos:

        if d[2] == 0:
            tree.insert("", "end", values=d, tags=("rojo",))
        else:
            tree.insert("", "end", values=d, tags=("amarillo",))

    # ===== BOTONES REPORTE =====

    crear_botones_reporte(win, tree, "REPORTE FALTANTE")
