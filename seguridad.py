from tkinter import messagebox

def acceso_modulo(nombre_modulo, LICENCIA):
    if nombre_modulo not in LICENCIA["modulos"]:
        messagebox.showwarning(
            "Módulo bloqueado",
            f"🔒 El módulo '{nombre_modulo}' no está disponible en tu plan.\n\nContacta para activarlo."
        )
        return False
    return True