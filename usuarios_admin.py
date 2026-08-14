from core import *
import sqlite3
import config
import hashlib
import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def abrir_usuarios(parent):

    # SOLO ADMIN
    if not config.es_admin():
        messagebox.showerror("Acceso", "Solo ADMIN puede administrar usuarios")
        return

    win = ctk.CTkToplevel(parent)
    win.title("Administrar Usuarios")

    win.state("zoomed")  # pantalla completa en Windows

    win.transient(parent)
    win.grab_set()

    frame = ctk.CTkFrame(win)
    frame.pack(fill="both", expand=True, padx=20, pady=55)

    ctk.CTkLabel(
        frame, text="👥 ADMINISTRAR USUARIOS", font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    # ================= BUSCADOR =================

    ctk.CTkLabel(frame, text="🔎 Buscar usuario").pack()

    entry_buscar = ctk.CTkEntry(frame, placeholder_text="Escriba para buscar...")
    entry_buscar.pack(fill="x", pady=5)
    entry_buscar.focus()

    ## ================= TABLA =================

    style = ttk.Style()
    style.theme_use("default")

    # style.configure(
    #    "Treeview",
    #    font=("Segoe UI", 11),
    #    rowheight=26,
    # )
    # """style.configure(
    #    "Treeview.Heading",
    #    font=("Segoe UI", 11, "bold"),
    # )"""

    style.configure("Usuarios.Treeview", font=("Segoe UI", 11), rowheight=26)
    style.configure("Usuarios.Treeview.Heading", font=("Segoe UI", 11, "bold"))

    tabla_frame = ctk.CTkFrame(frame)
    tabla_frame.pack(fill="both", expand=True, pady=10)

    tree = ttk.Treeview(
        tabla_frame,
        columns=("id", "usuario", "rol", "estado"),
        show="headings",
        style="Usuarios.Treeview",
    )

    tree.heading("id", text="ID", command=lambda: ordenar_col("id", False))
    tree.heading(
        "usuario", text="USUARIO", command=lambda: ordenar_col("usuario", False)
    )
    tree.heading("rol", text="ROL", command=lambda: ordenar_col("rol", False))
    tree.heading("estado", text="ESTADO", command=lambda: ordenar_col("estado", False))

    tree.column("id", width=70, anchor="center")
    tree.column("usuario", width=300)
    tree.column("rol", width=140, anchor="center")
    tree.column("estado", width=140, anchor="center")

    scroll = ttk.Scrollbar(tabla_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)

    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    # COLORES
    tree.tag_configure("activo", foreground="#0A7A2F")
    tree.tag_configure("inactivo", foreground="#B22222")
    tree.tag_configure("admin", background="#eef4ff")

    # ================= FUNCIONES =================

    def listar():

        tree.delete(*tree.get_children())

        conn = sqlite3.connect(DB_USUARIOS)
        cursor = conn.cursor()

        cursor.execute("SELECT id, usuario, rol, estado FROM usuarios")

        for fila in cursor.fetchall():

            estado = "ACTIVO" if fila[3] == 1 else "INACTIVO"

            if estado == "ACTIVO":
                tag = "activo"
            else:
                tag = "inactivo"

            if fila[2] == "ADMIN":
                tag = "admin"

            tree.insert(
                "", "end", values=(fila[0], fila[1], fila[2], estado), tags=(tag,)
            )

        conn.close()

    def ordenar_col(col, reverse):

        datos = [(tree.set(k, col), k) for k in tree.get_children("")]

        try:
            datos.sort(key=lambda t: int(t[0]), reverse=reverse)
        except:
            datos.sort(reverse=reverse)

        for index, (val, k) in enumerate(datos):
            tree.move(k, "", index)

        tree.heading(col, command=lambda: ordenar_col(col, not reverse))

        def buscar_usuario(event=None):

            texto = entry_buscar.get().strip()

            tree.delete(*tree.get_children())

            conn = sqlite3.connect(DB_USUARIOS)
            cursor = conn.cursor()

            if texto == "":
                cursor.execute("SELECT id, usuario, rol, estado FROM usuarios")
            else:
                cursor.execute(
                    "SELECT id, usuario, rol, estado FROM usuarios WHERE usuario LIKE ?",
                    ("%" + texto + "%",),
                )

            for fila in cursor.fetchall():

                estado = "ACTIVO" if fila[3] == 1 else "INACTIVO"
                tag = "activo" if estado == "ACTIVO" else "inactivo"

                tree.insert(
                    "", "end", values=(fila[0], fila[1], fila[2], estado), tags=(tag,)
                )

            conn.close()

        entry_buscar.bind("<KeyRelease>", buscar_usuario)

    # ================= NUEVO USUARIO =================

    def abrir_registro():

        reg = ctk.CTkToplevel(win)
        reg.title("Crear usuario")
        reg.geometry("350x300")
        reg.transient(win)
        reg.grab_set()

        ctk.CTkLabel(reg, text="Nuevo Usuario", font=("Segoe UI", 16, "bold")).pack(
            pady=10
        )

        entry_user = ctk.CTkEntry(reg, placeholder_text="Usuario")
        entry_user.pack(pady=5)

        entry_pass = ctk.CTkEntry(reg, placeholder_text="Clave", show="*")
        entry_pass.pack(pady=5)

        combo_rol = ctk.CTkComboBox(reg, values=["ADMIN", "VENDEDOR"])
        combo_rol.set("VENDEDOR")
        combo_rol.pack(pady=5)

        def guardar():

            user = entry_user.get().strip()
            clave = entry_pass.get().strip()
            rol = combo_rol.get()

            if not user or not clave:
                messagebox.showerror("Error", "Campos vacíos", parent=reg)
                return

            conn = sqlite3.connect(DB_USUARIOS)
            cursor = conn.cursor()

            try:

                cursor.execute(
                    """
                    INSERT INTO usuarios (usuario, clave, rol, estado)
                    VALUES (?, ?, ?, 1)
                    """,
                    (user, hash_password(clave), rol),
                )

                conn.commit()

                messagebox.showinfo("OK", "Usuario creado", parent=reg)

                reg.destroy()
                listar()

            except:
                messagebox.showerror("Error", "El usuario ya existe", parent=reg)

            conn.close()

        ctk.CTkButton(reg, text="Guardar", command=guardar).pack(pady=15)

    # ================= CAMBIAR ROL =================

    def cambiar_rol():

        item = tree.focus()
        if not item:
            return

        datos = tree.item(item)["values"]
        user_id = datos[0]

        conn = sqlite3.connect(DB_USUARIOS)
        cursor = conn.cursor()

        nuevo = "ADMIN" if datos[2] == "VENDEDOR" else "VENDEDOR"

        cursor.execute(
            "UPDATE usuarios SET rol=? WHERE id=?",
            (nuevo, user_id),
        )

        conn.commit()
        conn.close()

        listar()

    # ================= ACTIVAR / DESACTIVAR =================

    def activar_desactivar():

        item = tree.focus()
        if not item:
            return

        datos = tree.item(item)["values"]
        user_id = datos[0]

        conn = sqlite3.connect(DB_USUARIOS)
        cursor = conn.cursor()

        cursor.execute("SELECT estado FROM usuarios WHERE id=?", (user_id,))
        estado = cursor.fetchone()[0]

        nuevo = 0 if estado == 1 else 1

        cursor.execute(
            "UPDATE usuarios SET estado=? WHERE id=?",
            (nuevo, user_id),
        )

        conn.commit()
        conn.close()

        listar()

    # ================= RESET CLAVE =================

    def reset_clave():

        item = tree.focus()
        if not item:
            return

        datos = tree.item(item)["values"]
        user_id = datos[0]

        nueva = simpledialog.askstring(
            "Reset contraseña", "Nueva contraseña:", show="*", parent=win
        )

        if not nueva:
            return

        conn = sqlite3.connect(DB_USUARIOS)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE usuarios SET clave=? WHERE id=?",
            (hash_password(nueva), user_id),
        )

        conn.commit()
        conn.close()

        messagebox.showinfo("OK", "Contraseña actualizada", parent=win)

    # ================= ELIMINAR =================

    def eliminar_usuario():

        item = tree.focus()

        if not item:
            messagebox.showwarning("Atención", "Seleccione un usuario")
            return

        datos = tree.item(item)["values"]

        user_id = datos[0]
        usuario = datos[1]
        rol = datos[2]

        # evitar borrar ADMIN
        if rol.upper() == "ADMIN":
            messagebox.showwarning(
                "Atención", "El usuario ADMIN no puede ser eliminado", parent=win
            )
            return

        # evitar eliminar usuario actual
        if usuario.upper() == config.usuario_actual["usuario"].upper():
            # if usuario.strip().upper() == config.usuario_actual.strip().upper():
            messagebox.showwarning(
                "Atención",
                "No puedes eliminar el usuario con el que estás trabajando",
                parent=win,
            )
            return

        confirmar = messagebox.askyesno(
            "Eliminar", f"¿Eliminar usuario '{usuario}'?", parent=win
        )

        if not confirmar:
            return

        try:

            conn = sqlite3.connect(DB_USUARIOS)
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM usuarios WHERE id=?",
                (user_id,),
            )

            conn.commit()
            conn.close()

            messagebox.showinfo("OK", "Usuario eliminado", parent=win)

            listar()

        except Exception as e:
            messagebox.showerror("Error", str(e), parent=win)

    def editar_usuario(event=None):

        item = tree.focus()
        if not item:
            return

        datos = tree.item(item)["values"]

        user_id = datos[0]
        usuario_actual = datos[1]
        rol_actual = datos[2]
        estado_actual = datos[3]

        edit = ctk.CTkToplevel(win)
        edit.title("Editar Usuario")
        edit.geometry("350x320")
        edit.transient(win)
        edit.grab_set()

        ctk.CTkLabel(edit, text="Editar Usuario", font=("Segoe UI", 16, "bold")).pack(
            pady=10
        )

        entry_user = ctk.CTkEntry(edit)
        entry_user.insert(0, usuario_actual)
        entry_user.pack(pady=5)

        combo_rol = ctk.CTkComboBox(edit, values=["ADMIN", "VENDEDOR"])
        combo_rol.set(rol_actual)
        combo_rol.pack(pady=5)

        combo_estado = ctk.CTkComboBox(edit, values=["ACTIVO", "INACTIVO"])
        combo_estado.set(estado_actual)
        combo_estado.pack(pady=5)

        def guardar():

            nuevo_user = entry_user.get().strip()
            nuevo_rol = combo_rol.get()
            nuevo_estado = 1 if combo_estado.get() == "ACTIVO" else 0

            conn = sqlite3.connect(DB_USUARIOS)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE usuarios
                SET usuario=?, rol=?, estado=?
                WHERE id=?
                """,
                (nuevo_user, nuevo_rol, nuevo_estado, user_id),
            )

            conn.commit()
            conn.close()

            messagebox.showinfo("OK", "Usuario actualizado", parent=edit)

            edit.destroy()
            listar()

        ctk.CTkButton(edit, text="Guardar cambios", command=guardar).pack(pady=15)

    # ================= BOTONES =================

    btns = ctk.CTkFrame(frame)
    btns.pack(pady=10)

    ctk.CTkButton(btns, text="➕ Nuevo Usuario", command=abrir_registro).pack(
        side="left", padx=5
    )

    ctk.CTkButton(btns, text="🔄 Actualizar lista", command=listar).pack(
        side="left", padx=5
    )

    ctk.CTkButton(btns, text="🔁 Cambiar rol", command=cambiar_rol).pack(
        side="left", padx=5
    )

    ctk.CTkButton(
        btns, text="🔒 Activar / Desactivar", command=activar_desactivar
    ).pack(side="left", padx=5)

    ctk.CTkButton(btns, text="🔑 Reset contraseña", command=reset_clave).pack(
        side="left", padx=5
    )

    ctk.CTkButton(btns, text="🗑 Eliminar usuario", command=eliminar_usuario).pack(
        side="left", padx=5
    )

    ctk.CTkButton(btns, text="✏ Editar usuario", command=editar_usuario).pack(
        side="left", padx=5
    )

    listar()
