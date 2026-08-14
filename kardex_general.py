from core import *
from config import *
from utils.centrar_ventana import centrar_ventana

def abrir_kardex_general(parent):

    win = tk.Toplevel(parent)
    win.title("Kardex General")
    win.transient(parent)
    win.grab_set()
    win.focus_force()
    win.lift()

    centrar_ventana(win, 1000, 600)

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

    columnas = ("fecha", "codigo", "descripcion", "tipo", "entrada", "salida")

    tree = ttk.Treeview(win, columns=columnas, show="headings")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    crear_botones_reporte(win, tree, "KARDEX GENERAL")

    tree.heading("fecha", text="Fecha")
    tree.heading("codigo", text="Código")
    tree.heading("descripcion", text="Producto")
    tree.heading("tipo", text="Tipo")
    tree.heading("entrada", text="Entrada")
    tree.heading("salida", text="Salida")

    tree.column("fecha", width=120)
    tree.column("codigo", width=80)
    tree.column("descripcion", width=250)
    tree.column("tipo", width=100)
    tree.column("entrada", width=100, anchor="e")
    tree.column("salida", width=100, anchor="e")

    # ================== CARGAR ==================

    def cargar():

        tree.delete(*tree.get_children())

        desde = entry_desde.get().strip()
        hasta = entry_hasta.get().strip()

        movimientos = []

        # -------- COMPRAS --------

        conn = sqlite3.connect(DB_COMPRAS)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT 
            c.fecha,
            d.codigo,
            d.descripcion,
            'COMPRA',
            d.cantidad,
            0
            FROM detalle_compra d
            JOIN compras c ON d.id_compra = c.id
        """
        )

        movimientos += cur.fetchall()
        conn.close()

        # -------- VENTAS --------


        conv = sqlite3.connect(DB_VENTAS)
        cur = conv.cursor()

        cur.execute(
            """
            SELECT 
            v.fecha,
            d.codigo,
            d.descripcion,
            'VENTA',
            0,
            d.cantidad
            FROM detalle_venta d
            JOIN ventas v ON d.id_venta = v.id
        """
        )

        movimientos += cur.fetchall()
        conv.close()
        
        # -------- ENTRADAS --------

        conn = sqlite3.connect(DB_ENTRADAS)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT 
            c.fecha,
            d.codigo,
            d.descripcion,
            'ENTRADA',
            d.cantidad,
            0
            FROM detalle_compra d
            JOIN compras c ON d.id_compra = c.id
        """
        )

        movimientos += cur.fetchall()
        conn.close()

        # -------- SALIDA --------


        conv = sqlite3.connect(DB_SALIDAS)
        cur = conv.cursor()

        cur.execute(
            """
            SELECT 
            v.fecha,
            d.codigo,
            d.descripcion,
            'SALIDA',
            0,
            d.cantidad
            FROM detalle_venta d
            JOIN ventas v ON d.id_venta = v.id
        """
        )

        movimientos += cur.fetchall()
        conv.close()
        
        
        # -------- ORDENAR --------

        movimientos.sort(key=lambda x: datetime.strptime(x[0][:10], "%Y-%m-%d"))

        # -------- MOSTRAR --------

        for mov in movimientos:

            fecha, codigo, descripcion, tipo, entrada, salida = mov

            if desde and fecha[:10] < desde:
                continue

            if hasta and fecha[:10] > hasta:
                continue

            tree.insert("", "end", values=mov)

    # ================== BOTONES ==================

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)

    tk.Button(btn_frame, text="Mostrar", command=cargar, bg="#3498db", fg="white").pack(
        side="left", padx=5
    )

    def ver_todo():
        entry_desde.delete(0, "end")
        entry_hasta.delete(0, "end")
        cargar()

    tk.Button(
        btn_frame, text="Ver Todo", command=ver_todo, bg="#2ecc71", fg="white"
    ).pack(side="left", padx=5)
