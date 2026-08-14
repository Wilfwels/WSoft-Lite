from core import *
from config import *
from utils.busqueda_productos import buscar_producto_ui
from utils.centrar_ventana import centrar_ventana


def abrir_kardex(menu):

    win = tk.Toplevel(menu)
    win.title("Kardex por Producto")
    win.transient(menu)
    win.grab_set()
    win.focus_force()
    win.lift()

    centrar_ventana(win, 1050, 600)

    codigo_seleccionado = {"valor": None}

    # ================= BUSQUEDA PRODUCTO =================
    frame_busqueda = tk.Frame(win)
    frame_busqueda.pack(fill="x", padx=10, pady=5)

    tk.Label(frame_busqueda, text="Buscar Producto Código / Descripción:").pack(
        side="left"
    )

    entry_buscar = tk.Entry(frame_busqueda, width=30)
    entry_buscar.pack(side="left", padx=5)

    tree_bus = ttk.Treeview(
        win, columns=("codigo", "descripcion"), show="headings", height=5
    )
    tree_bus.heading("codigo", text="Código")
    tree_bus.heading("descripcion", text="Descripción")
    tree_bus.pack(fill="x", padx=10)

    # ================= BUSCAR EN BD =================
    def buscar_producto_db(txt):

        conn = sqlite3.connect(DB_INV)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT codigo, descripcion
            FROM inventario
            WHERE codigo LIKE ? OR descripcion LIKE ?
            """,
            (f"%{txt}%", f"%{txt}%"),
        )

        resultados = cur.fetchall()
        conn.close()
        return resultados

    entry_buscar.bind(
        "<KeyRelease>",
        lambda e: buscar_producto_ui(entry_buscar, tree_bus, buscar_producto_db),
    )

    # ================= ENCABEZADO PRODUCTO =================
    frame_info = tk.Frame(win)
    frame_info.pack(fill="x", padx=10, pady=5)

    lbl_titulo = tk.Label(
        frame_info, text="KARDEX DEL PRODUCTO", font=("Arial", 14, "bold")
    )
    lbl_titulo.pack()

    lbl_producto = tk.Label(frame_info, text="", font=("Arial", 11))
    lbl_producto.pack()

    # ================= FILTRO FECHAS =================
    frame_fechas = tk.Frame(win)
    frame_fechas.pack(fill="x", padx=10, pady=5)

    tk.Label(frame_fechas, text="Desde (YYYY-MM-DD):").pack(side="left")
    entry_desde = tk.Entry(frame_fechas, width=12)
    entry_desde.pack(side="left", padx=5)

    tk.Label(frame_fechas, text="Hasta (YYYY-MM-DD):").pack(side="left")
    entry_hasta = tk.Entry(frame_fechas, width=12)
    entry_hasta.pack(side="left", padx=5)

    # ================= TREE KARDEX =================
    columnas = ("fecha", "tipo", "doc", "entrada", "salida", "saldo")

    tree = ttk.Treeview(win, columns=columnas, show="headings")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    crear_botones_reporte(win, tree, "KARDEX")

    for col in columnas:
        tree.heading(col, text=col.capitalize())
        tree.column(col, anchor="center")

    # ================= TOTALES =================
    frame_totales = tk.Frame(win)
    frame_totales.pack(fill="x", padx=10, pady=5)

    lbl_total_entradas = tk.Label(frame_totales, text="Total Entradas: 0")
    lbl_total_entradas.pack(side="left", padx=20)

    lbl_total_salidas = tk.Label(frame_totales, text="Total Salidas: 0")
    lbl_total_salidas.pack(side="left", padx=20)

    lbl_saldo_final = tk.Label(
        frame_totales, text="Saldo Final: 0", font=("Arial", 12, "bold"), fg="green"
    )
    lbl_saldo_final.pack(side="right", padx=20)

    # ================= CARGAR KARDEX =================
    def cargar_kardex():

        codigo = codigo_seleccionado["valor"]
        if not codigo:
            return

        desde = entry_desde.get().strip()
        hasta = entry_hasta.get().strip()

        tree.delete(*tree.get_children())
        movimientos = []
        
        """"""
        # COMPRAS
        #conn = sqlite3.connect(DB_COMPRAS)
        #cur = conn.cursor()
        #cur.execute(
        # 
        #    SELECT c.fecha,'COMPRA',c.id,dc.cantidad,0
        #    FROM detalle_compra dc
        #    JOIN compras c ON dc.id_compra=c.id
        #    WHERE dc.codigo=?
        #    """,
        #    (codigo,),
        #)
        #movimientos += cur.fetchall()
        #conn.close()

        # VENTAS
        #conn = sqlite3.connect(DB_VENTAS)
        #cur = conn.cursor()
        #cur.execute(
        #    """
        #    SELECT v.fecha,'VENTA',v.id,0,dv.cantidad
        #    FROM detalle_venta dv
        #    JOIN ventas v ON dv.id_venta=v.id
        #    WHERE dv.codigo=?
        #    """,
        #    (codigo,),
        #)
        #movimientos += cur.fetchall()
        #conn.close() 
        

        # MOVIMIENTOS
        conn = sqlite3.connect(DB_MOVIMI)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
            fecha,
            tipo,
            referencia,
            CASE
                WHEN tipo IN ('COMPRA','ENTRADA MANUAL')
                THEN cantidad
                ELSE 0
            END AS entrada,
            CASE
                WHEN tipo IN ('VENTA','SALIDA MANUAL')
                THEN cantidad
                ELSE 0
            END AS salida
            FROM movimientos
            WHERE producto_id = ?
            """,
            (codigo,),
        )
        movimientos += cur.fetchall()
        conn.close()

        movimientos.sort(key=lambda x: datetime.strptime(x[0][:10], "%Y-%m-%d"))

        saldo = 0
        total_entradas = 0
        total_salidas = 0

        for fecha, tipo, doc, entrada, salida in movimientos:

            fecha_mov = datetime.strptime(fecha[:10], "%Y-%m-%d")

            if desde:
                if fecha_mov < datetime.strptime(desde, "%Y-%m-%d"):
                    continue

            if hasta:
                if fecha_mov > datetime.strptime(hasta, "%Y-%m-%d"):
                    continue

            saldo += entrada
            saldo -= salida

            total_entradas += entrada
            total_salidas += salida

            tree.insert("", "end", values=(fecha, tipo, doc, entrada, salida, saldo))

        lbl_total_entradas.config(text=f"Total Entradas: {total_entradas}")
        lbl_total_salidas.config(text=f"Total Salidas: {total_salidas}")
        lbl_saldo_final.config(text=f"Saldo Final: {saldo}")

        if saldo < 0:
            lbl_saldo_final.config(fg="red")
        else:
            lbl_saldo_final.config(fg="green")

    # ================= BOTONES FILTRO =================
    def ver_todo():
        entry_desde.delete(0, "end")
        entry_hasta.delete(0, "end")
        cargar_kardex()

    tk.Button(
        frame_fechas, text="Mostrar", command=cargar_kardex, bg="#3498db", fg="white"
    ).pack(side="left", padx=5)

    tk.Button(
        frame_fechas, text="Ver Todo", command=ver_todo, bg="#2ecc71", fg="white"
    ).pack(side="left", padx=5)

    # ================= SELECCIONAR PRODUCTO =================
    def seleccionar_producto(event=None):

        item = tree_bus.selection()
        if not item:
            return

        valores = tree_bus.item(item)["values"]
        codigo = valores[0]
        descripcion = valores[1]

        codigo_seleccionado["valor"] = codigo

        lbl_producto.config(text=f"Código: {codigo} | Descripción: {descripcion}")

        entry_buscar.delete(0, tk.END)
        tree_bus.delete(*tree_bus.get_children())

        cargar_kardex()

    tree_bus.bind("<Double-1>", seleccionar_producto)
    tree_bus.bind("<Return>", seleccionar_producto)

    # ================= NAVEGACION =================
    def bajar_tree(event):
        items = tree_bus.get_children()
        if items:
            tree_bus.focus(items[0])
            tree_bus.selection_set(items[0])
            tree_bus.focus_set()
        return "break"

    entry_buscar.bind("<Down>", bajar_tree)

    def enter_desde_entry(event):
        items = tree_bus.get_children()
        if items:
            tree_bus.focus(items[0])
            tree_bus.selection_set(items[0])
            seleccionar_producto()
        return "break"

    entry_buscar.bind("<Return>", enter_desde_entry)

