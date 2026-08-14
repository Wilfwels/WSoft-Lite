from core import *
from config import *
from utils.centrar_ventana import centrar_ventana

def abrir_kardex_total(parent):

    win = tk.Toplevel(parent)
    win.title("Kardex Total")
    win.transient(parent)
    win.grab_set()
    win.focus_force()
    win.lift()

    centrar_ventana(win, 1000, 600)

    # ================== TREEVIEW ==================

    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    columnas = ("codigo", "descripcion", "entradas", "salidas", "saldo")

    tree = ttk.Treeview(frame, columns=columnas, show="headings")

    crear_botones_reporte(win, tree, "KARDEX TOTAL")

    tree.heading("codigo", text="Código")
    tree.heading("descripcion", text="Descripción")
    tree.heading("entradas", text="Entradas")
    tree.heading("salidas", text="Salidas")
    tree.heading("saldo", text="Saldo")

    tree.column("codigo", width=120)
    tree.column("descripcion", width=350)
    tree.column("entradas", width=100, anchor="center")
    tree.column("salidas", width=100, anchor="center")
    tree.column("saldo", width=100, anchor="center")

    tree.pack(fill="both", expand=True)

    # ================== TOTALES ==================

    frame_totales = tk.Frame(win)
    frame_totales.pack(fill="x", padx=10, pady=5)

    lbl_total_entradas = tk.Label(frame_totales, text="Total Entradas: 0")
    lbl_total_entradas.pack(side="left", padx=10)

    lbl_total_salidas = tk.Label(frame_totales, text="Total Salidas: 0")
    lbl_total_salidas.pack(side="left", padx=10)

    lbl_total_saldo = tk.Label(frame_totales, text="Saldo Total: 0")
    lbl_total_saldo.pack(side="left", padx=10)

    # ================== CARGAR DATOS ==================

    def cargar_reporte():

        tree.delete(*tree.get_children())

        conn = sqlite3.connect(DB_INV)
        cur = conn.cursor()

        cur.execute("SELECT codigo, descripcion FROM inventario")
        productos = cur.fetchall()
        conn.close()

        total_entradas = 0
        total_salidas = 0
        total_saldo = 0

        for codigo, descripcion in productos:

            entradas = 0
            salidas = 0
            
            # -------- MOVIMIENTOS --------

            conn = sqlite3.connect(DB_MOVIMI)
            cur = conn.cursor()

            cur.execute(
                """
                SELECT tipo, SUM(cantidad)
                FROM movimientos
                WHERE producto_id = ?
                GROUP BY tipo
                """,
                (codigo,),
            )

            movimientos = cur.fetchall()

            for tipo, cant in movimientos:

                if tipo in ("COMPRA", "ENTRADA MANUAL"):
                    entradas += cant

                if tipo in ("VENTA", "SALIDA MANUAL"):
                    salidas += cant

            conn.close()

            saldo = entradas - salidas

            total_entradas += entradas
            total_salidas += salidas
            total_saldo += saldo

            tree.insert(
                "",
                "end",
                values=(codigo, descripcion, entradas, salidas, saldo),
            )

        lbl_total_entradas.config(text=f"Total Entradas: {total_entradas}")
        lbl_total_salidas.config(text=f"Total Salidas: {total_salidas}")
        lbl_total_saldo.config(text=f"Saldo Total: {total_saldo}")

    cargar_reporte()
