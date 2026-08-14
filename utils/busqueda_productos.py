def buscar_producto_ui(
    entry_buscar,
    tree_bus,
    buscar_producto_db,
    btn_producto=None,
    permitir_crear=True,
):
    tree_bus.delete(*tree_bus.get_children())
    txt = entry_buscar.get().strip()

    if not txt:
        if btn_producto:
            btn_producto.pack_forget()
        return

    resultados = buscar_producto_db(txt)

    # 🚫 NO HAY RESULTADOS
    if not resultados:

        tree_bus.insert(
            "",
            "end",
            values=("", "Producto no existe (F4 para crear)", "", "", ""),
            tags=("no_existe",),
        )

        tree_bus.tag_configure("no_existe", foreground="red")

        if permitir_crear and btn_producto:
            btn_producto.pack(side="left", padx=8)

        return

    # ✅ SI HAY RESULTADOS
    if btn_producto:
        btn_producto.pack_forget()

    for fila in resultados:
        tree_bus.insert("", "end", values=fila)
