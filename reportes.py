import customtkinter as ctk
from tkinter import ttk

import inventario_valorizado


def abrir_reportes(menu):

    win = ctk.CTkToplevel(menu)
    win.title("Reportes WSoft")
    win.geometry("400x400")

    frame = ctk.CTkFrame(win)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    titulo = ctk.CTkLabel(frame, text="CENTRO DE REPORTES", font=("Arial", 18, "bold"))
    titulo.pack(pady=20)

    # ==========================
    # INVENTARIO
    # ==========================

    btn_inv_val = ctk.CTkButton(
        frame,
        text="Inventario Valorizado",
        width=250,
        command=lambda: inventario_valorizado.abrir_inventario_valorizado(win),
    )
    btn_inv_val.pack(pady=10)

    # futuros reportes

    btn_kardex = ctk.CTkButton(
        frame, text="Kardex Producto", width=250, state="disabled"
    )
    btn_kardex.pack(pady=10)

    btn_ventas = ctk.CTkButton(
        frame, text="Ventas por Fecha", width=250, state="disabled"
    )
    btn_ventas.pack(pady=10)
