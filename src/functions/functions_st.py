import csv
from pathlib import Path
from utils.constantes import PROJECT_PATH
import pandas as pd

def obtener_primer_trimestre_y_anio(hogares, personas):
    """
    Devuelve el año y trimestre más viejo de los archivos de hogares e individuos.
    Args: Recibe como parámetro los 2 datasets (lista de diccionarios) de hogares e individuos para recorrer
    Retorna: Una tupla que contiene el año ("ANO4") y el trimestre ("TRIMESTRE") más recientes.
    """
    trimestres = set()
    # Recorremos ambos conjuntos (hogares y personas) para agregar los años y trimestres disponibles
    for row in hogares + personas:
        trimestres.add((int(row["ANO4"]), int(row["TRIMESTRE"])))
    # Encontramos el año más reciente después de recorrer todos los trimestres
    primer_anio = min([anio for anio, trimestre in trimestres])
    # Filtramos los trimestres correspondientes al último año
    trimestres_primer_anio = []
    for anio, trim in trimestres:
        if anio == primer_anio:
            trimestres_primer_anio.append(trim)
    # Encontramos el trimestre más reciente de ese año
    primer_trimestre = min(trimestres_primer_anio)
    return primer_trimestre, primer_anio

def cargar_datos_hogares():
    """Carga un archivo CSV en un DataFrame de pandas.

    Returns:
        pd.DataFrame: DataFrame con los datos del archivo."""
    #calculo la ruta
    ruta_csv =  PROJECT_PATH / "files_out" / "usu_hogares.csv"
    return cargar_datos(ruta_csv)

def cargar_datos_ind():
    """Carga un archivo CSV en un DataFrame de pandas.
    Returns:
        pd.DataFrame: DataFrame con los datos del archivo."""
    #calculo la ruta
    ruta_csv =  PROJECT_PATH / "files_out" / "usu_individuales.csv"
    return cargar_datos(ruta_csv)    

def cargar_datos(ruta_csv):
    """Carga un archivo CSV en un DataFrame de pandas.
    Returns:
        pd.DataFrame: DataFrame con los datos del archivo."""
    # Cargar los datos, read_csv convierte a dataframe
    return pd.read_csv(ruta_csv, sep=';', low_memory=False)