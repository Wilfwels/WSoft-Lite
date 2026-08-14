from core import *
from config import *
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportes_utils import crear_botones_reporte
from reportes_utils import exportar_excel


def abrir_inventario_valorizado(parent):

    win = tk.Toplevel(parent)
    win.title("Inventario Valorizado")
    win.geometry("900x500")

    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ================== TREEVIEW ==================

    columnas = ("codigo", "descripcion", "cantidad", "costo", "total")

    tree = ttk.Treeview(frame, columns=columnas, show="headings")

    tree.heading("codigo", text="Código")
    tree.heading("descripcion", text="Descripción")
    tree.heading("cantidad", text="Cantidad")
    tree.heading("costo", text="Costo")
    tree.heading("total", text="Valor Total")

    tree.column("codigo", width=100)
    tree.column("descripcion", width=400)
    tree.column("cantidad", width=100, anchor="center")
    tree.column("costo", width=120, anchor="e")
    tree.column("total", width=150, anchor="e")

    tree.pack(fill="both", expand=True)

    crear_botones_reporte(win, tree, "INVENTARIO VALORIZADO")

    # ================== TOTAL ==================

    lbl_total = tk.Label(
        win, text="Total Inventario: 0", font=("Arial", 12, "bold"), fg="blue"
    )
    lbl_total.pack(pady=5)

    # ================== CARGAR INVENTARIO ==================

    def cargar_inventario():

        tree.delete(*tree.get_children())

        conn = sqlite3.connect(DB_INV)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT codigo, descripcion, cantidad, costo
            FROM inventario
            ORDER BY descripcion
        """
        )

        filas = cur.fetchall()
        conn.close()

        total_general = 0

        for codigo, descripcion, cantidad, costo in filas:

            cantidad = cantidad or 0
            costo = costo or 0

            total = cantidad * costo
            total_general += total

            tree.insert(
                "",
                "end",
                values=(
                    codigo,
                    descripcion,
                    cantidad,
                    f"{costo:,.2f}",
                    f"{total:,.2f}",
                ),
            )

        lbl_total.config(text=f"Total Inventario: {total_general:,.2f}")

    # ================== INICIO ==================

    cargar_inventario()
