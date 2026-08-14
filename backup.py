def crear_backup(carpeta_destino):

    import os
    import shutil
    from datetime import datetime
    from config import DATA_DIR

    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    carpeta_backup = os.path.join(
        carpeta_destino,
        "WSoft_Backup_" + fecha
    )

    os.makedirs(
        carpeta_backup,
        exist_ok=True
    )

    archivos = [
        f for f in os.listdir(DATA_DIR)
        if f.endswith(".db")
    ]


    for archivo in archivos:

        origen = os.path.join(
            DATA_DIR,
            archivo
        )

        destino = os.path.join(
            carpeta_backup,
            archivo
        )

        shutil.copy2(
            origen,
            destino
        )


    return True, carpeta_backup

def restaurar_backup(ruta_backup, callback=None):

    import os
    import shutil
    from config import DATA_DIR

    try:

        # 🔥 borrar bases actuales
        for archivo in os.listdir(DATA_DIR):

            if archivo.endswith(".db"):

                ruta_db = os.path.join(DATA_DIR, archivo)

                try:
                    os.remove(ruta_db)
                except:
                    pass

        # 🔥 copiar backup
        archivos = [
            f for f in os.listdir(ruta_backup)
            if f.endswith(".db")
        ]

        total = len(archivos)

        for i, archivo in enumerate(archivos, start=1):

            origen = os.path.join(ruta_backup, archivo)
            destino = os.path.join(DATA_DIR, archivo)

            shutil.copy2(origen, destino)

            if callback:
                progreso = int((i / total) * 100)
                callback(progreso, archivo)

        return True, "Restauración completada"

    except Exception as e:
        return False, str(e)

