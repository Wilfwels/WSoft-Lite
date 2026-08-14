from core import *
from config import *
from utils.centrar_ventana import centrar_ventana


# ================== UTILIDADES ==================
def formato_moneda(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def abrir_reporte_totales_vendedores(parent):

    win = tk.Toplevel(parent)
    win.title("Totales por Vendedor")
    win.transient(parent)
    win.grab_set()
    win.focus_force()
    win.lift()

    centrar_ventana(win, 900, 550)

    # ================== FILTRO ==================

    frame_filtro = tk.Frame(win)
    frame_filtro.pack(fill="x", padx=10, pady=5)

    tk.Label(frame_filtro, text="Desde (YYYY-MM-DD):").pack(side="left")

    entry_desde = tk.Entry(frame_filtro, width=12)
    entry_desde.pack(side="left", padx=5)

    tk.Label(frame_filtro, text="Hasta (YYYY-MM-DD):").pack(side="left")

    entry_hasta = tk.Entry(frame_filtro, width=12)
    entry_hasta.pack(side="left", padx=5)

    # ================== TREE ==================

    columnas = ("codigo", "vendedor", "facturas", "total")

    tree = ttk.Treeview(win, columns=columnas, show="headings")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    tree.heading("codigo", text="Código")
    tree.heading("vendedor", text="Vendedor")
    tree.heading("facturas", text="Facturas")
    tree.heading("total", text="Total Vendido")

    tree.column("codigo", width=80, anchor="center")
    tree.column("vendedor", width=300)
    tree.column("facturas", width=100, anchor="center")
    tree.column("total", width=150, anchor="e")

    crear_botones_reporte(win, tree, "TOTALES POR VENDEDOR")

    # ================== CARGAR ==================

    def cargar():

        tree.delete(*tree.get_children())

        desde = entry_desde.get().strip()
        hasta = entry_hasta.get().strip()

        conn = sqlite3.connect(DB_VENTAS)
        cur = conn.cursor()

        sql = """
        SELECT
            vendedor_codigo,
            COUNT(id),
            SUM(total)
        FROM ventas
        WHERE 1=1
        """

        parametros = []

        if desde:
            sql += " AND substr(fecha,1,10) >= ?"
            parametros.append(desde)

        if hasta:
            sql += " AND substr(fecha,1,10) <= ?"
            parametros.append(hasta)

        sql += """
        GROUP BY vendedor_codigo
        ORDER BY SUM(total) DESC
        """

        cur.execute(sql, parametros)

        datos = cur.fetchall()

        conn.close()

        conn = sqlite3.connect(DB_VENDE)
        cur = conn.cursor()

        total_facturas = 0
        total_general = 0

        for codigo, facturas, total in datos:

            cur.execute(
                "SELECT nombre FROM vendedores WHERE codigo=?",
                (codigo,),
            )

            fila = cur.fetchone()

            nombre = fila[0] if fila else "SIN VENDEDOR"

            tree.insert(
                "",
                "end",
                values=(
                    codigo if codigo else "---",
                    nombre,
                    facturas,
                    formato_moneda(total),
                ),
            )

            total_facturas += facturas
            total_general += total

        conn.close()

        tree.insert(
            "",
            "end",
            values=(
                "",
                "TOTAL GENERAL",
                total_facturas,
                formato_moneda(total_general),
            ),
        )

    # ================== BOTONES ==================

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)

    tk.Button(
        btn_frame,
        text="Mostrar",
        command=cargar,
        bg="#3498db",
        fg="white",
    ).pack(side="left", padx=5)

    def ver_todo():
        entry_desde.delete(0, "end")
        entry_hasta.delete(0, "end")
        cargar()

    tk.Button(
        btn_frame,
        text="Ver Todo",
        command=ver_todo,
        bg="#2ecc71",
        fg="white",
    ).pack(side="left", padx=5)