from core import *
from config import *
from utils.centrar_ventana import centrar_ventana


# ================== UTILIDADES ==================
def formato_moneda(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def abrir_reporte_vendedores(parent):

    win = tk.Toplevel(parent)
    win.title("Reporte de Ventas por Vendedor")
    win.transient(parent)
    win.grab_set()
    win.focus_force()
    win.lift()

    centrar_ventana(win, 950, 550)


    # ================== FILTRO ==================

    frame_filtro = tk.Frame(win)
    frame_filtro.pack(fill="x", padx=10, pady=5)


    tk.Label(
        frame_filtro,
        text="Desde (YYYY-MM-DD):"
    ).pack(side="left")

    entry_desde = tk.Entry(frame_filtro, width=12)
    entry_desde.pack(side="left", padx=5)


    tk.Label(
        frame_filtro,
        text="Hasta (YYYY-MM-DD):"
    ).pack(side="left")

    entry_hasta = tk.Entry(frame_filtro, width=12)
    entry_hasta.pack(side="left", padx=5)



    # ================== TREE ==================

    columnas = (
        "fecha",
        "codigo",
        "vendedor",
        "ventas",
        "total"
    )


    tree = ttk.Treeview(
        win,
        columns=columnas,
        show="headings"
    )

    tree.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )


    tree.heading("fecha", text="Fecha")
    tree.heading("codigo", text="Código")
    tree.heading("vendedor", text="Vendedor")
    tree.heading("ventas", text="Cantidad Ventas")
    tree.heading("total", text="Total Vendido")


    tree.column("fecha", width=120)
    tree.column("codigo", width=80, anchor="center")
    tree.column("vendedor", width=280)
    tree.column("ventas", width=120, anchor="center")
    tree.column("total", width=150, anchor="e")


    crear_botones_reporte(
        win,
        tree,
        "REPORTE VENTAS VENDEDORES"
    )



    # ================== CARGAR ==================

    def cargar():

        tree.delete(*tree.get_children())


        desde = entry_desde.get().strip()
        hasta = entry_hasta.get().strip()


        movimientos = []


        # ===== VENTAS =====

        conn = sqlite3.connect(DB_VENTAS)
        cur = conn.cursor()


        cur.execute("""
            SELECT
                substr(v.fecha,1,10),
                v.vendedor_codigo,
                COUNT(v.id),
                SUM(v.total)
            FROM ventas v
            GROUP BY
                substr(v.fecha,1,10),
                v.vendedor_codigo
            ORDER BY
                v.fecha
        """)


        datos = cur.fetchall()

        conn.close()



        # ===== BUSCAR NOMBRE VENDEDOR =====

        conn = sqlite3.connect(DB_VENDE)
        cur = conn.cursor()


        for fecha, codigo, cantidad, total in datos:


            if desde and fecha < desde:
                continue

            if hasta and fecha > hasta:
                continue


            cur.execute(
                """
                SELECT nombre
                FROM vendedores
                WHERE codigo = ?
                """,
                (codigo,)
            )


            vendedor = cur.fetchone()


            nombre = (
                vendedor[0]
                if vendedor
                else "SIN VENDEDOR"
            )


            tree.insert(
                "",
                "end",
                values=(
                    fecha,
                    codigo if codigo else "---",
                    nombre,
                    cantidad,
                    formato_moneda(total)
                )
            )


        conn.close()



    # ================== BOTONES ==================

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)


    tk.Button(
        btn_frame,
        text="Mostrar",
        command=cargar,
        bg="#3498db",
        fg="white"
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
        fg="white"
    ).pack(side="left", padx=5)