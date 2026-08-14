import sys
import os

def obtener_ruta_base():
    # Si está compilado (.exe)
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # Si está en desarrollo (.py)
    return os.path.dirname(os.path.abspath(__file__))

def ruta_archivo(nombre):
    return os.path.join(obtener_ruta_base(), nombre)