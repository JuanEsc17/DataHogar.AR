import pandas as pd
import sys
from pathlib import Path
import streamlit as st
import json
import folium
from streamlit_folium import folium_static

src_path = Path(__file__).resolve().parents[2]

sys.path.append(str(src_path))
from utils.constantes import NIVEL_EDUCATIVO_ID_A_NOMBRE, AGLOMERADO_ID_A_NOMBRE

def personas_desocupadas_estudios(anio, trimestre):
    """
    Devuelve la cantidad de personas desocupadas agrupadas por nivel educativo.

    Args:
        anio (int): Año a consultar.
        trimestre (int): Trimestre a consultar.

    Returns:
        dict: Un diccionario donde las claves son niveles educativos y los valores son cantidades de personas desocupadas.
    """
    file_path = Path(__file__).resolve().parents[3] / 'files_out' / 'usu_individuales.csv'

    # Cargar el dataset (el dtype={102: str} es para que la columna 102 se convierta a string)
    df = pd.read_csv(file_path, delimiter=';', encoding='utf-8', dtype={102: str})

    # Filtro el DataFrame para quedarse solo con las filas que cumplan con el año y trimestre ingresados
    # y que la columna ESTADO sea igual a 2 (desocupados)
    df_filtrado = df[
        (df['ANO4'] == int(anio)) &
        (df['TRIMESTRE'] == int(trimestre)) &
        (df['ESTADO'] == 2)
    ]

    # Agrupo por el nivel educativo y sumo la columna PONDERA
    resultado = df_filtrado.groupby('NIVEL_ED')['PONDERA'].sum()

    # Convierto los IDs de nivel educativo a nombres
    desocupados = {}
    for nivel in resultado.index:
        nombre_nivel = NIVEL_EDUCATIVO_ID_A_NOMBRE.get(str(nivel), f"Nivel desconocido ({nivel})")
        desocupados[nombre_nivel] = int(resultado[nivel])
    return desocupados

def tasa_desempleo_empleo(aglomerado):
    """
    Calcula la tasa de desempleo y empleo por aglomerado y por período.

    Args:
        aglomerado (str): ID del aglomerado (usar "0" para incluir todos).

    Returns:
        pd.DataFrame: DataFrame con las tasas de empleo y desempleo por período.
    """
    df = pd.read_csv(
        Path(__file__).resolve().parents[3] / 'files_out' / 'usu_individuales.csv',
        delimiter=';',
        encoding='utf-8',
        dtype={102: str}
    )

    # Creo una columna "PERIODO" que concatena el año y el trimestre
    df["PERIODO"] = df["ANO4"].astype(str) + ", T" + df["TRIMESTRE"].astype(str)

    # Si se eligio un aglomerado distinto de "0", filtro el DataFrame
    # para quedarme solo con las filas que tengan el ID_AGLOMERADO correspondiente
    if aglomerado != "0":
        df = df[
            df["AGLOMERADO"] == int(aglomerado)
        ]
    # Si se eligio "0", no filtro por aglomerado
    # Filtro el DataFrame para quedarme con las filas que tengan Ocupacion y las que tengan Desocupacion
    df = df[
     df["ESTADO"].isin([1, 2])
    ]

    # Mapear ESTADO a nombres legibles (1: ocupado, 2: desocupado)
    df["ESTADO_LABEL"] = df["ESTADO"].map({1: "ocupado", 2: "desocupado"})

    # Agrupo por "PERIODO" y "ESTADO" y cuento la cantidad de filas
    resumen = df.groupby(["PERIODO", "ESTADO_LABEL"]).size().unstack(fill_value=0)

    # Calculo el porcentaje de desocupados
    resumen["Tasa desempleo"] = round(((
    resumen["desocupado"] / (resumen["ocupado"] + resumen["desocupado"])
    ) * 100), 2)

    # Calculo el porcentaje de ocupados
    resumen["Tasa empleo"] = round(((
    resumen["ocupado"] / (resumen["desocupado"] + resumen["ocupado"])
    ) * 100), 2)

    resumen = resumen.reset_index()
    return resumen

def porcentajes_empleo():
    """
    Calcula los porcentajes de tipos de empleo (estatal, privado y otros) para cada aglomerado.

    Returns:
        pd.DataFrame: DataFrame con los porcentajes de empleo por tipo y aglomerado.
    """
    df = pd.read_csv(
        Path(__file__).resolve().parents[3] / 'files_out' / 'usu_individuales.csv',
        delimiter=';',
        encoding='utf-8',
        dtype={102: str}
    )

    # Filtro el DataFrame para quedarme solo con las filas que tengan Ocupacion
    df = df[
        df["ESTADO"] == 1
    ]

    # Agrupo por "AGLOMERADO" y "OCUPACION" y cuento la cantidad de filas
    resumen = df.groupby(["AGLOMERADO", "PP04A"]).size().unstack(fill_value=0)

    # Borro la columa con clave 9 (no se sabe que es)
    resumen = resumen.drop(columns=9)

    # Agrego una columna "Total" que sume los valores de cada fila (axis=1 hace que sume por fila, axis=0 lo hace por columna)
    resumen["Total"] = resumen.sum(axis=1)
    resumen[1] = round(resumen[1]/resumen["Total"] * 100, 2)
    resumen[2] = round(resumen[2]/resumen["Total"] * 100, 2)
    resumen[3] = round(resumen[3]/resumen["Total"] * 100, 2)

    # Renombro las columnas 1, 2 y 3
    resumen = resumen.rename(columns={
        1: "Empleo estatal",
        2: "Empleo privado",
        3: "Otro tipo"
    })

    # Agrego una columna con el nombre del aglomerado
    resumen["Nombre aglomerado"] = resumen.index.map(lambda x: AGLOMERADO_ID_A_NOMBRE.get(str(x), f"Aglomerado {x}"))

    # Reordeno las columnas para que "Nombre aglomerado" sea la primera
    cols = list(resumen.columns)
    cols.insert(0, cols.pop(cols.index("Nombre aglomerado")))
    resumen = resumen[cols]

    # Cambia el índice a "Nombre aglomerado" y elimina la columna del índice anterior
    resumen = resumen.set_index("Nombre aglomerado")

    return resumen

def obtener_desempleo_empleo_mapa(tipo="Empleo"):
    """
    Obtiene las tasas de empleo o desempleo por aglomerado para dos períodos, útil para visualizaciones en mapa.

    Args:
        tipo (str, optional): "Empleo" o "Desempleo". Por defecto es "empleo".

    Returns:
        pd.DataFrame: DataFrame con tasa inicial, final y cambio por aglomerado, más un color asociado.
    """


    primer_trimestre, primer_anio = st.session_state.tri_anio_min
    ultimo_trimestre, ultimo_anio = st.session_state.tri_anio_max

    df = pd.read_csv(
        Path(__file__).resolve().parents[3] / 'files_out' / 'usu_individuales.csv',
        delimiter=';',
        encoding='utf-8',
        dtype={102: str}
    )

    # Filtrar por ocupados y desocupados
    df = df[df["ESTADO"].isin([1, 2])]
    df["PERIODO"] = df["ANO4"].astype(str) + ", T" + df["TRIMESTRE"].astype(str)
    df["ESTADO_LABEL"] = df["ESTADO"].map({1: "ocupado", 2: "desocupado"})

    resumen = []

    # Definir periodos a analizar
    periodo_ini = f"{primer_anio}, T{primer_trimestre}"
    periodo_fin = f"{ultimo_anio}, T{ultimo_trimestre}"

    for aglomerado, nombre in AGLOMERADO_ID_A_NOMBRE.items():
        df_aglo = df[df["AGLOMERADO"] == int(aglomerado)]

        resumen_periodo = df_aglo.groupby(["PERIODO", "ESTADO"]).size().unstack(fill_value=0)

        if periodo_ini not in resumen_periodo.index or periodo_fin not in resumen_periodo.index:
            continue  # Saltar si falta algún periodo

        ini_ocu = resumen_periodo.loc[periodo_ini].get(1, 0)
        ini_des = resumen_periodo.loc[periodo_ini].get(2, 0)
        fin_ocu = resumen_periodo.loc[periodo_fin].get(1, 0)
        fin_des = resumen_periodo.loc[periodo_fin].get(2, 0)

        if (ini_ocu + ini_des == 0) or (fin_ocu + fin_des == 0):
            continue  # Evitar división por cero

        tasa_ini = ini_ocu / (ini_ocu + ini_des) * 100 if tipo == "Empleo" else ini_des / (ini_ocu + ini_des) * 100
        tasa_fin = fin_ocu / (fin_ocu + fin_des) * 100 if tipo == "Empleo" else fin_des / (fin_ocu + fin_des) * 100

        if tipo == "Empleo":
            # Para empleo: aumento es bueno (verde), disminución es malo (rojo)
            cambio = "Aumentó" if tasa_fin > tasa_ini else "Disminuyó o igual"
            color = "green" if tasa_fin > tasa_ini else "red"
        else:  # Desempleo
            # Para desempleo: aumento es malo (rojo), disminución es bueno (verde)
            cambio = "Aumentó" if tasa_fin > tasa_ini else "Disminuyó o igual"
            color = "green" if tasa_fin > tasa_ini else "red"

        resumen.append({
            "Nombre aglomerado": nombre,
            "Tasa inicial": round(tasa_ini, 2),
            "Tasa final": round(tasa_fin, 2),
            "Cambio": cambio,
            "Color": color
        })

    resumen  = pd.DataFrame(resumen)

    return resumen

def mostrar_mapa(resultado):
    """
    Muestra un mapa interactivo con la evolución de tasas por aglomerado.

    Usa coordenadas predefinidas para ubicar marcadores en un mapa de Argentina.
    Cada marcador muestra la tasa inicial y final, y se colorea según el cambio.

    Args:
        resultado (pd.DataFrame): DataFrame que contiene columnas:
            - 'Nombre aglomerado' (str): Nombre del aglomerado.
            - 'Tasa inicial' (float): Tasa en el primer período.
            - 'Tasa final' (float): Tasa en el último período.
            - 'Color' (str): Color del marcador ('red' o 'green').

    Returns:
        None: La función no retorna nada, muestra el mapa con `folium_static`.
    """
    file_path = Path(__file__).resolve().parents[3] / 'files' / 'aglomerados_coordenadas.json'
    # Cargar las coordenadas de los aglomerados desde el archivo JSON
    with open(file_path, 'r', encoding='utf-8') as f:
        coords = json.load(f)
    # Crear un diccionario con los nombres de los aglomerados y sus coordenadas
    coord_dict = {v["nombre"]: v["coordenadas"] for v in coords.values()}
    # Crear un mapa centrado en Argentina
    m = folium.Map(location=[-38.5, -63.0], zoom_start=4.5)
    for _, row in resultado.iterrows():
        nombre = row["Nombre aglomerado"]
        color_row = row["Color"]
        tasa_ini = row["Tasa inicial"]
        tasa_fin = row["Tasa final"]

        if nombre in coord_dict:
            lat, lon = coord_dict[nombre]
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(f"<b>{nombre}</b><br>Tasa inicial: {tasa_ini}%<br>Tasa final: {tasa_fin}%", max_width=200),
                icon=folium.Icon(color=color_row)
            ).add_to(m)

    folium_static(m)