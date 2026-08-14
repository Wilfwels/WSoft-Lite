import hashlib
import platform
import uuid
import os


def obtener_id_hardware():

    datos = []

    # Nombre del equipo
    datos.append(platform.node())

    # Sistema operativo
    datos.append(platform.system())

    # Identificador MAC
    datos.append(str(uuid.getnode()))


    cadena = "|".join(datos)


    # Creamos huella única
    hash_hw = hashlib.sha256(
        cadena.encode()
    ).hexdigest()


    # Tomamos solo una parte para hacerlo manejable
    hardware_id = hash_hw[:16].upper()


    return hardware_id



if __name__ == "__main__":

    print(
        "ID EQUIPO:",
        obtener_id_hardware()
    )