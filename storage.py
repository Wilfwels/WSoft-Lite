import json
import os
from datetime import datetime
from config import VERSION, PRODUCTO

def guardar_json(ruta, datos):

    with open(
        ruta,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            datos,
            archivo,
            indent=4,
            ensure_ascii=False
        )



def leer_json(ruta):

    if not os.path.exists(ruta):
        return None


    with open(
        ruta,
        "r",
        encoding="utf-8"
    ) as archivo:

        return json.load(archivo)



def crear_system(
        ruta,
        hardware_id
    ):


    datos = {

        "instalado":
            datetime.now().strftime("%Y-%m-%d"),

        "primer_inicio":
            datetime.now().strftime("%Y-%m-%d"),

        "hardware":
            hardware_id,

        "contador":
            1,

        "version":
            VERSION,

        "producto":
            PRODUCTO

    }

    guardar_json(
        ruta,
        datos
    )

    def actualizar_system(ruta, sistema):

        sistema["contador"] = (
            sistema.get("contador", 0) + 1
        )

        guardar_json(
            ruta,
            sistema
        )

        return sistema

    return datos