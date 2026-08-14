import os
import json

from datetime import datetime, timedelta

from config import LICENCIA_FILE, SYSTEM_FILE

from hardware import obtener_id_hardware

from crypto import (
    validar_firma,
    generar_firma
)

from storage import (
    leer_json,
    crear_system
)


def cargar_licencia():

    if not os.path.exists(LICENCIA_FILE):
        return None

    return leer_json(
        LICENCIA_FILE
    )



def crear_licencia_demo(sistema):

    datos = {

        "cliente": "EVALUACION",

        "plan": "DEMO",

        "hardware":
            sistema["hardware"],

        "vence":
            (
                datetime.now()
                +
                timedelta(days=10)
            ).strftime("%Y-%m-%d")

    }


    datos["firma"] = generar_firma(datos)


    with open(
        LICENCIA_FILE,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            datos,
            archivo,
            indent=4,
            ensure_ascii=False
        )


    return datos



def inicializar_sistema():

    sistema = leer_json(
        SYSTEM_FILE
    )


    if sistema is None:

        hardware = obtener_id_hardware()

        sistema = crear_system(
            SYSTEM_FILE,
            hardware
        )


    return sistema



def verificar_licencia():

    sistema = inicializar_sistema()


    licencia = cargar_licencia()


    # ==================================
    # PRIMERA EJECUCIÓN
    # ==================================

    if licencia is None:

        licencia = crear_licencia_demo(
            sistema
        )


        fecha = datetime.strptime(
            licencia["vence"],
            "%Y-%m-%d"
        )

        dias = (
            fecha.date()
            -
            datetime.now().date()
        ).days


        return {

            "estado":
                "DEMO",

            "plan":
                "DEMO",

            "cliente":
                licencia["cliente"],

            "vence":
                licencia["vence"],

            "dias":
                dias,

            "mensaje":
                "Modo demo activo"

        }



    # ==================================
    # VALIDAR FIRMA
    # ==================================

    firma = licencia.get(
        "firma"
    )


    datos = licencia.copy()


    datos.pop(
        "firma",
        None
    )


    if not validar_firma(
        datos,
        firma
    ):

        return {

            "estado":
                "BLOQUEADA",

            "mensaje":
                "Licencia inválida"

        }



    # ==================================
    # VALIDAR HARDWARE
    # ==================================

    if licencia.get(
        "hardware"
    ) != sistema.get(
        "hardware"
    ):

        return {

            "estado":
                "BLOQUEADA",

            "mensaje":
                "Licencia pertenece a otro equipo"

        }



    # ==================================
    # VALIDAR FECHA
    # ==================================

    fecha = datetime.strptime(
        licencia["vence"],
        "%Y-%m-%d"
    )

    dias = (
        fecha.date()
        -
        datetime.now().date()
    ).days


    if datetime.now() > fecha:

        return {

            "estado":
                "VENCIDA",

            "plan":
                licencia.get("plan"),

            "dias":
                0,

            "mensaje":
                "Licencia vencida"

        }



    # ==================================
    # DEMO
    # ==================================

    if licencia.get("plan") == "DEMO":

        return {

            "estado":
                "DEMO",

            "plan":
                "DEMO",

            "cliente":
                licencia.get("cliente"),

            "vence":
                licencia.get("vence"),

            "dias":
                dias,

            "mensaje":
                "Modo demo activo"

        }



    # ==================================
    # LICENCIA ACTIVA
    # ==================================

    return {

        "estado":
            "ACTIVA",

        "plan":
            licencia.get("plan"),

        "cliente":
            licencia.get("cliente"),

        "vence":
            licencia.get("vence"),

        "dias":
            dias,

        "mensaje":
            "Licencia correcta"

    }