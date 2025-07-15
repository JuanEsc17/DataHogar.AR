import csv
from pathlib import Path
import pandas as pd

def obtener_anio_trimestre(path_archivo):
    """
    Lee un archivo y extrae los valores de las columnas 'ANO4' y 'TRIMESTRE'.
    Parámetros:
    - path_archivo: ruta del archivo.
    Retorna:
    - (anio, trimestre) como strings, o (None, None) si hay error.
    """
    try:
        # Intenta leer el archivo como CSV separado por ';'
        df = pd.read_csv(path_archivo, sep=";", low_memory=False)
        #low_memory en false es para evitar errores o advertencias de pandas.
        # Extrae el primer valor de las columnas 'ANO4' y 'TRIMESTRE'
        anio = str(df["ANO4"].iloc[0])
        trimestre = str(df["TRIMESTRE"].iloc[0])
        return anio, trimestre
    except Exception as e:
        # Si hay un error (archivo malformado, columnas faltantes, etc)
        print(f"Error al leer {path_archivo.name}: {e}")
        return None, None
    
def chequeo_archivos_por_contenido(path_files):
    """
    Verifica que por cada archivo de hogares exista uno de individuales y viceversa,
    basándose en el contenido de las columnas ANO4 y TRIMESTRE.
    Parámetros:
    - path_files: ruta a la carpeta que contiene los archivos .txt
    Retorna:
    - Lista de tuplas con faltantes: (año, trimestre, tipo_faltante)
    """
    carpeta = Path(path_files)  # Convierte la ruta en objeto Path
    hogares = {}                # Diccionario para guardar archivos de hogares
    individuales = {}           # Diccionario para guardar archivos de individuales

    # Itera sobre todos los archivos .txt en la carpeta
    for archivo in carpeta.glob("*.txt"):
        anio, trimestre = obtener_anio_trimestre(archivo)
        if anio and trimestre:
            clave = (anio, trimestre)
            nombre = archivo.name.lower()
            # Clasifica el archivo según su nombre (hogares o individuales)
            if "hogar" in nombre:
                hogares[clave] = archivo.name
            elif "individual" in nombre:
                individuales[clave] = archivo.name

    #Creo una lista para guardarme los faltantes si es que existen
    faltantes = []
    # Crea un conjunto con todas las combinaciones (año, trimestre) encontradas (tupla)
    claves = set(hogares.keys()).union(individuales.keys())

    # Verifica si falta algún tipo por cada clave
    for clave in claves:
        #si para esta combinación de año y trimestre(clave)no hay un archivo :
        if clave not in hogares:
            #agrego agrego un registro a la lista faltantes con el año (clave[0]), 
            # el trimestre (clave[1]), y el tipo de archivo que falta
            faltantes.append((clave[0], clave[1], "hogares"))
        if clave not in individuales:
            faltantes.append((clave[0], clave[1], "individuales"))

    return faltantes