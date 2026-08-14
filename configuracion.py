import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import os
from licencias import verificar_licencia
from PIL import Image
from utils import centrar_ventana
from config import *
import shutil

def abrir_configuracion(parent):

    win = ctk.CTkToplevel(parent)
    win.title("Configuración de Empresa")
    win.resizable(False, False)
    win.grab_set()

    centrar_ventana(win, 580, 820)

    # ===== CENTRAR CONTENIDO =====
    win.grid_rowconfigure(0, weight=1)
    win.grid_columnconfigure(0, weight=1)

    main_frame = ctk.CTkFrame(win)
    main_frame.grid(row=0, column=0)

    # ===== FUNCIÓN PARA FILAS COMPACTAS =====
    def fila(label_text):
        frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        frame.pack(pady=4)

        label = ctk.CTkLabel(frame, text=label_text, width=150, anchor="e")
        label.pack(side="left", padx=8)

        entry = ctk.CTkEntry(frame, width=280)
        entry.pack(side="left")

        return entry

    entry_nombre = fila("Nombre Empresa:")
    entry_rif = fila("RIF / NIT:")
    entry_direccion = fila("Dirección:")
    entry_telefono = fila("Teléfono:")
    entry_correo = fila("Correo:")
    entry_impuesto = fila("Impuesto (%):")
    
    # ===================================
    # CONFIGURACION DE VENTAS
    # ===================================

    impresion_venta = tk.StringVar(
        value="PREGUNTAR"
    )

    abrir_pdf_venta = tk.BooleanVar(
        value=False
    )


    frame_impresion = ctk.CTkFrame(
        main_frame
    )

    frame_impresion.pack(
        pady=10,
        padx=20,
        fill="x"
    )


    ctk.CTkLabel(
        frame_impresion,
        text="Configuración de ventas",
        font=("Arial", 14, "bold")
    ).pack(
        pady=5
    )


    opciones = [
        (
            "Preguntar al finalizar venta",
            "PREGUNTAR"
        ),
        (
            "Ticket automático",
            "TICKET"
        ),
        (
            "Factura automática",
            "FACTURA"
        ),
        (
            "No imprimir",
            "NADA"
        )
    ]


    for texto, valor in opciones:

        ctk.CTkRadioButton(
            frame_impresion,
            text=texto,
            variable=impresion_venta,
            value=valor
        ).pack(
            anchor="w",
            padx=30,
            pady=2
        )


    ctk.CTkCheckBox(
        frame_impresion,
        text="Abrir PDF automáticamente",
        variable=abrir_pdf_venta
    ).pack(
        pady=8
    )

    # ===== MENSAJE =====
    ctk.CTkLabel(main_frame, text="Mensaje pie de ticket:").pack(pady=(8, 2))
    entry_mensaje = ctk.CTkTextbox(main_frame, width=420, height=60)
    entry_mensaje.pack(pady=4)

    # ===== LOGO =====
    ctk.CTkLabel(main_frame, text="Logo de la empresa").pack(pady=(10, 2))

    frame_logo = ctk.CTkFrame(main_frame)
    frame_logo.pack(pady=4)

    logo_path = tk.StringVar()

    label_logo = ctk.CTkLabel(frame_logo, text="Sin logo seleccionado")
    label_logo.pack()

    preview_logo = ctk.CTkLabel(frame_logo, text="")
    preview_logo.pack(pady=4)

    def seleccionar_logo():
        ruta = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg")]
        )
        if ruta:
            logo_path.set(ruta)
            label_logo.configure(text=os.path.basename(ruta))
            try:
                img = Image.open(ruta)
                img = img.resize((100, 100))
                logo_img = ctk.CTkImage(light_image=img, size=(100, 100))
                preview_logo.configure(image=logo_img)
                preview_logo.image = logo_img
            except:
                messagebox.showerror("Error", "No se pudo cargar la imagen")

    boton_logo = ctk.CTkButton(
        frame_logo,
        text="Seleccionar Logo",
        width=150,
        command=seleccionar_logo
    )

    boton_logo.pack(pady=4)
    
    licencia = verificar_licencia()

    if licencia["estado"] == "DEMO":

        boton_logo.configure(
            state="disabled"
        )
          
    # ===== CARGAR DATOS =====
    conn = sqlite3.connect(DB_EMPRESA)
    cur = conn.cursor()
    cur.execute("SELECT * FROM empresa LIMIT 1")
    data = cur.fetchone()
    conn.close()

    if data:
        (
            _,
            nombre,
            rif,
            direccion,
            telefono,
            correo,
            logo,
            mensaje,
            impuesto,
            impresion_guardada,
            pdf_guardado
        ) = data
        
        entry_nombre.insert(0, nombre or "")
        entry_rif.insert(0, rif or "")
        entry_direccion.insert(0, direccion or "")
        entry_telefono.insert(0, telefono or "")
        entry_correo.insert(0, correo or "")
        entry_impuesto.insert(0, impuesto or 0)
        entry_mensaje.insert("1.0", mensaje or "")
        impresion_venta.set(
            impresion_guardada or "PREGUNTAR"
        )
        
        abrir_pdf_venta.set(
            bool(pdf_guardado)
        )
        if logo:

            logo_path.set(logo)

            label_logo.configure(
                text=os.path.basename(logo)
            )

            try:

                ruta_logo = os.path.join(
                    LOGOS_DIR,
                    logo
                )

                img = Image.open(ruta_logo)
                img = img.resize((100, 100))

                logo_img = ctk.CTkImage(
                    light_image=img,
                    size=(100, 100)
                )

                preview_logo.configure(
                    image=logo_img
                )

                preview_logo.image = logo_img

            except Exception as e:
                print("Error cargando logo:", e)

    # ===== GUARDAR =====
    def guardar():

        try:
            impuesto = float(entry_impuesto.get() or 0)

        except ValueError:
            messagebox.showerror(
                "Error",
                "Impuesto inválido"
            )
            return


        # ===============================
        # GUARDAR LOGO
        # ===============================


        logo_guardar = logo_path.get()

        if logo_guardar and licencia["estado"] != "DEMO":

            try:
                # Si viene una ruta completa del selector
                if os.path.exists(logo_guardar):

                    nombre_logo = "empresa_logo.png"

                    destino = os.path.join(
                        LOGOS_DIR,
                        nombre_logo
                    )

                    shutil.copy(
                        logo_guardar,
                        destino
                    )

                    # En BD guardamos SOLO el nombre
                    logo_guardar = nombre_logo

            except Exception as e:

                messagebox.showerror(
                    "Error Logo",
                    str(e)
                )
                return


        datos = (
            entry_nombre.get(),
            entry_rif.get(),
            entry_direccion.get(),
            entry_telefono.get(),
            entry_correo.get(),
            logo_guardar,
            entry_mensaje.get("1.0", "end").strip(),
            impuesto,
            impresion_venta.get(),
            1 if abrir_pdf_venta.get() else 0
        )


        conn = sqlite3.connect(DB_EMPRESA)
        cur = conn.cursor()


        cur.execute(
            "SELECT id FROM empresa LIMIT 1"
        )

        existe = cur.fetchone()


        if existe:

            cur.execute(
                """
                UPDATE empresa SET
                    nombre=?,
                    rif=?,
                    direccion=?,
                    telefono=?,
                    correo=?,
                    logo=?,
                    mensaje_ticket=?,
                    impuesto_defecto=?,
                    impresion_venta=?,
                    abrir_pdf_venta=?
                WHERE id=?
                """,
                (*datos, existe[0]),
            )


        else:

            cur.execute(
                """
                INSERT INTO empresa
                (nombre, rif, direccion, telefono, correo, logo, mensaje_ticket, impuesto_defecto, impresion_venta,abrir_pdf_venta)
                VALUES (?,?,?,?,?,?,?,?,?,?)
                """,
                datos,
            )


        conn.commit()
        conn.close()


        messagebox.showinfo(
            "Configuración",
            "Datos guardados correctamente"
        )


    # ===== BOTÓN GUARDAR =====
    ctk.CTkButton(
        main_frame,
        text="💾 Guardar",
        width=200,
        command=guardar
    ).pack(pady=15)

            