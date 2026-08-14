import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

from main import crear_backup, restaurar_backup  # tus funciones
from config import BASE_DIR


class PanelTecnico:

    def __init__(self, root):
        self.root = root
        self.root.title("Panel Técnico Wsoft")
        self.root.geometry("420x300")
        self.root.resizable(False, False)

        # 🔹 Título
        titulo = tk.Label(root, text="Mantenimiento del Sistema", font=("Arial", 12, "bold"))
        titulo.pack(pady=10)

        # 🔹 Barra progreso
        self.progress = ttk.Progressbar(root, length=350, mode='determinate')
        self.progress.pack(pady=10)

        # 🔹 Texto estado
        self.label_estado = tk.Label(root, text="Listo", anchor="w")
        self.label_estado.pack(fill="x", padx=20)

        # 🔹 Botones
        frame_botones = tk.Frame(root)
        frame_botones.pack(pady=20)

        btn_backup = tk.Button(frame_botones, text="💾 Crear Backup", width=18, command=self.iniciar_backup)
        btn_backup.grid(row=0, column=0, padx=5, pady=5)

        btn_restaurar = tk.Button(frame_botones, text="♻️ Restaurar Backup", width=18, command=self.iniciar_restauracion)
        btn_restaurar.grid(row=0, column=1, padx=5, pady=5)

    # 🔥 ACTUALIZA BARRA
    def actualizar_barra(self, valor, archivo):
        self.progress["value"] = valor
        self.label_estado.config(text=f"{valor}% - {archivo}")
        self.root.update_idletasks()

    # 💾 BACKUP
    def iniciar_backup(self):
        self.progress["value"] = 0
        self.label_estado.config(text="Iniciando backup...")

        def tarea():
            ok, msg = crear_backup(callback=self.actualizar_barra)
            self.label_estado.config(text=msg)
            messagebox.showinfo("Backup", msg)

        threading.Thread(target=tarea, daemon=True).start()

    # 🔄 RESTAURAR
    def iniciar_restauracion(self):
        ruta = filedialog.askdirectory(title="Seleccionar carpeta de backup")

        if not ruta:
            return

        confirm = messagebox.askyesno(
            "Confirmar",
            "⚠️ Esto reemplazará los datos actuales.\n¿Deseas continuar?"
        )

        if not confirm:
            return

        self.progress["value"] = 0
        self.label_estado.config(text="Restaurando...")

        def tarea():
            ok, msg = restaurar_backup(ruta, callback=self.actualizar_barra)
            self.label_estado.config(text=msg)
            messagebox.showinfo("Restauración", msg)

        threading.Thread(target=tarea, daemon=True).start()


# 🚀 EJECUTAR PANEL
if __name__ == "__main__":
    root = tk.Tk()
    app = PanelTecnico(root)
    root.mainloop()