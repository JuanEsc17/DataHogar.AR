import csv
import pandas as pd
def obtener_ultimo_trimestre_y_anio_archivos(file_path):
    """
    Devuelve el año y trimestre más recientes de los archivos de hogares e individuos.
    Args: Recibe como parámetro los 2 datasets (lista de diccionarios) de hogares e individuos para recorrer
    Retorna: Una tupla que contiene el año ("ANO4") y el trimestre ("TRIMESTRE") más recientes.
    """
    trimestres = set()
    # Recorremos ambos conjuntos (hogares y personas) para agregar los años y trimestres disponibles
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            trimestres.add((int(row["ANO4"]), int(row["TRIMESTRE"])))
        # Encontramos el año más reciente después de recorrer todos los trimestres
        ultimo_anio = max([anio for anio, trimestre in trimestres])
        # Filtramos los trimestres correspondientes al último año
    trimestres_ultimo_anio = []
    for anio, trim in trimestres:
        if anio == ultimo_anio:
            trimestres_ultimo_anio.append(trim)
    # Encontramos el trimestre más reciente de ese año
    ultimo_trimestre = max(trimestres_ultimo_anio)
    return ultimo_trimestre, ultimo_anio

# Reutilizar
def obtener_ultimo_trimestre_y_anio(file_path_personas,file_path_hogares):
    """
    Devuelve el año y trimestre más recientes de los archivos de hogares e individuos.
    Args: Recibe como parámetro los 2 datasets (lista de diccionarios) de hogares e individuos para recorrer
    Retorna: Una tupla que contiene el año ("ANO4") y el trimestre ("TRIMESTRE") más recientes.
    """
    ult_trim_hog, ult_anio_hog = obtener_ultimo_trimestre_y_anio_archivos(file_path_hogares)
    ult_trim_per, ult_anio_per = obtener_ultimo_trimestre_y_anio_archivos(file_path_personas)

    if (ult_trim_hog, ult_anio_hog) != (ult_trim_per, ult_anio_per):
        print(f"Los últimos trimestres y años de los archivos no coinciden:")
    else:
        ult_anio = ult_anio_hog
        ult_tri = ult_trim_hog
    return ult_tri, ult_anio


def obtener_primer_trimestre_y_anio_archivos(file_path):
    """
    Devuelve el año y trimestre más recientes de los archivos de hogares e individuos.
    Args: Recibe como parámetro los 2 datasets (lista de diccionarios) de hogares e individuos para recorrer
    Retorna: Una tupla que contiene el año ("ANO4") y el trimestre ("TRIMESTRE") más recientes.
    """
    trimestres = set()
    # Recorremos ambos conjuntos (hogares y personas) para agregar los años y trimestres disponibles
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            trimestres.add((int(row["ANO4"]), int(row["TRIMESTRE"])))
        # Encontramos el año más reciente después de recorrer todos los trimestres
        ultimo_anio = min([anio for anio, trimestre in trimestres])
        # Filtramos los trimestres correspondientes al último año
    trimestres_ultimo_anio = []
    for anio, trim in trimestres:
        if anio == ultimo_anio:
            trimestres_ultimo_anio.append(trim)
    # Encontramos el trimestre más reciente de ese año
    ultimo_trimestre = min(trimestres_ultimo_anio)
    return ultimo_trimestre, ultimo_anio

# Reutilizar
def obtener_primer_trimestre_y_anio(file_path_personas,file_path_hogares):
    """
    Devuelve el año y trimestre más recientes de los archivos de hogares e individuos.
    Args: Recibe como parámetro los 2 datasets (lista de diccionarios) de hogares e individuos para recorrer
    Retorna: Una tupla que contiene el año ("ANO4") y el trimestre ("TRIMESTRE") más recientes.
    """
    pri_trim_hog, pri_anio_hog = obtener_primer_trimestre_y_anio_archivos(file_path_hogares)
    pri_trim_per, pri_anio_per = obtener_primer_trimestre_y_anio_archivos(file_path_personas)

    if (pri_trim_hog, pri_anio_hog) != (pri_trim_per, pri_anio_per):
        print(f"Los últimos trimestres y años de los archivos no coinciden:")
    else:
        pri_anio = pri_anio_hog
        pri_tri = pri_trim_hog
    return pri_tri, pri_anio

# Validar año

def validar_anio(anio, df):
    anios_disponibles = df["ANO4"].unique()
    if anio not in anios_disponibles:
        return None, f"El año ingresado ({anio}) no está disponible."
    return anio, None

# obtener ultimo trimestre a partir de un año ingresado 
def obtener_ultimo_trimestre(anio,file_path):
    trimestres_disponibles = set()
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row["ANO4"] == str(anio):
                try:
                    trimestres_disponibles.add(int(row["TRIMESTRE"]))
                except ValueError:
                    continue
        if not trimestres_disponibles:
            print(f"No se encontraron registros para el año {anio}.")
            return
        return max(trimestres_disponibles)
    
def validar_trimestre_disponible(df, anio, trimestre):
    """
    Verifica si el trimestre ingresado está disponible para el año dado en el DataFrame.
    
    Parámetros:
        df : pandas.DataFrame
            DataFrame con columnas 'ANO4' y 'TRIMESTRE'.
        anio : int
            Año a verificar.
        trimestre : int
            Trimestre a verificar (1-4).
    
    Retorna:
        (bool, str or None)
        True y None si es válido, False y un mensaje de error si no.
    """
    trimestres_disponibles = df.loc[df["ANO4"] == anio, "TRIMESTRE"].unique()
    if trimestre not in trimestres_disponibles:
        return False, f"El trimestre ingresado ({trimestre}) no está disponible para el año {anio}."
    return True, None