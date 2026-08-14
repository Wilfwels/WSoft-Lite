def centrar_ventana(win, width, height):
    win.update_idletasks()

    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)

    win.geometry(f"{width}x{height}+{x}+{y}")
