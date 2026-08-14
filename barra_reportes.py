import customtkinter as ctk
from tkinter import messagebox


def barra_reportes(
    parent, tree=None, ver=None, imprimir=None, pdf=None, excel=None, guardar=None
):

    frame = ctk.CTkFrame(parent)
    frame.pack(fill="x", pady=6, padx=6)

    # ==============================
    # VALIDAR SI HAY DATOS
    # ==============================

    def hay_datos():

        if tree is None:
            return True

        if not tree.get_children():
            messagebox.showwarning("Aviso", "No hay datos para procesar.")
            return False

        return True

    # ==============================
    # BOTON VER TODO
    # ==============================

    def accion_ver():

        if ver:
            ver()

    # ==============================
    # BOTON IMPRIMIR
    # ==============================

    def accion_imprimir():

        if not hay_datos():
            return

        if messagebox.askyesno("Confirmar", "¿Desea imprimir el reporte?"):

            if imprimir:
                imprimir()

    # ==============================
    # BOTON PDF
    # ==============================

    def accion_pdf():

        if not hay_datos():
            return

        if messagebox.askyesno("Confirmar", "¿Exportar reporte a PDF?"):

            if pdf:
                pdf()

    # ==============================
    # BOTON EXCEL
    # ==============================

    def accion_excel():

        if not hay_datos():
            return

        if messagebox.askyesno("Confirmar", "¿Exportar reporte a Excel?"):

            if excel:
                excel()

    # ==============================
    # BOTON GUARDAR
    # ==============================

    def accion_guardar():

        if not hay_datos():
            return

        if messagebox.askyesno("Confirmar", "¿Guardar reporte?"):

            if guardar:
                guardar()

    # ==============================
    # BOTONES
    # ==============================

    ctk.CTkButton(frame, text="Ver Todo", width=120, command=accion_ver).pack(
        side="left", padx=4
    )

    ctk.CTkButton(frame, text="Imprimir", width=120, command=accion_imprimir).pack(
        side="left", padx=4
    )

    ctk.CTkButton(frame, text="Exportar PDF", width=140, command=accion_pdf).pack(
        side="left", padx=4
    )

    ctk.CTkButton(frame, text="Exportar Excel", width=140, command=accion_excel).pack(
        side="left", padx=4
    )

    ctk.CTkButton(frame, text="Guardar", width=120, command=accion_guardar).pack(
        side="left", padx=4
    )

    return frame
