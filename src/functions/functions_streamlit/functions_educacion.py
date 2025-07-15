import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from utils.constantes import PROJECT_PATH
from utils.constantes import CH12_ID_A_NOMBRE, INTERVALOS_ETARIOS_EDUCACION
from functions.functions_st import cargar_datos_hogares, cargar_datos_ind
from functions.functions_B import ranking_aglomerados

def filtrar_datos(df,anio):
    """Filtra un DataFrame por el año especificado y guarda solo las columnas necesarias
    Parámetros:
        df (pd.DataFrame): DataFrame a filtrar.
        anio (int): Año por el que filtrar.
    Returns:
        pd.DataFrame: DataFrame filtrado por el año especificado y guardada solo lo que se necesita, si no se puede convertir a int devuelve None"""
    try:
        # y si no se puede convertir a int también nulo
        anio = int(anio)
    except Exception:
        return None
    #filtro por el año pasado
    df_anio = df[df["ANO4"]==anio]
    # Agrupar por nivel educativo y contar devuelve una serie
    nivel_educ = df_anio.groupby("CH12")["PONDERA"].sum().reset_index()   
    return nivel_educ
def grafico_maximo_nivel_educativo_alcanzado():

    """Genera un gráfico de barras del máximo nivel educativo alcanzado por los encuestados.
    Parámetros:
        df (pd.DataFrame): DataFrame con los datos a graficar.
    """
    # Cargar los datos
    anios = st.session_state["trimestres_por_año"].keys()
    anio = st.selectbox("Elige un año:", anios)
    #botoncito que informa cuando lo tocas
    if st.button("Informar", key="grafico_maximo_nivel"):
        df = cargar_datos_ind()
    # filtrar los años es válidos
        df_filtrado = filtrar_datos(df,anio)
        if informar_no_hay_datos(df_filtrado):
            return
        #saco las filas donde CH12 es 0 o 99 xq no se sabe que son
        df_filtrado = df_filtrado[~df_filtrado["CH12"].isin([0, 99])]
        #cambio el nombre de la columna CH12 por el nombre del nivel educativo
        df_filtrado["Nivel educativo"] = df_filtrado["CH12"].map(CH12_ID_A_NOMBRE)
        #hago el grafico con streamlit   
        st.bar_chart(df_filtrado.set_index("Nivel educativo")[["PONDERA"]], x_label="Nivel Educativo", y_label="Cantidad de personas", stack=False)
def agrupar_por_grupo_etario(df, intervalo):
    """Agrupa un DataFrame por grupo etario y calcula la suma de ponderaciones.

    Parámetros:
        df (pd.DataFrame): DataFrame a agrupar.
        intervalo (list): Lista de intervalos etarios a filtrar.

    Retorna:
        pd.DataFrame: DataFrame filtrado con una nueva columna 'Rango Etario' que indica el intervalo etario.
    """
    # Crear la columna 'Rango Etario' como None inicialmente
    df["Rango Etario"] = None

    if "Todos" in intervalo:
        # Si se selecciona "Todos", asignar el rango etario correspondiente a cada fila
        df["Rango Etario"] = pd.cut(
            df["CH06"],
            bins=[0, 18, 25, 35, 45, 60, float("inf")],
            labels=["Menores de 18", "18 a 24", "25 a 34", "35 a 44", "45 a 59", "Más de 60"],
            right=False
        )
        return df
    else:
        # Dejar filtros en None para saber cuándo empieza a filtrar
        filtros = None

        # Como pueden ser varios intervalos, recorro con un for
        for i in intervalo:
            # Si es "Más de 60", agarro los mayores de 60
            if i == "Más de 60":
                condicion = (df["CH06"] > 60)
                df.loc[condicion, "Rango Etario"] = "Más de 60"
            else:
                # Si no es "Más de 60", agarro cada valor del intervalo
                edad_min, edad_max = map(int, i.split(" a "))
                condicion = ((df["CH06"] >= edad_min) & (df["CH06"] <= edad_max))
                df.loc[condicion, "Rango Etario"] = i
            # Filtro el DataFrame por la condición
            filtros = condicion if filtros is None else filtros | condicion

        # Filtrar el DataFrame por los intervalos seleccionados
        df = df.loc[filtros]
    return df

def informar_nivel_mas_comun():
    """
    Calcula el nivel educativo más común por rango etario seleccionado y lo informa con gráficos individuales.
    
    Retorna:
        No retorna nada, solo muestra el resultado en la interfaz de Streamlit.
    """
    # Guardar el intervalo etario en una variable
    intervalo = st.multiselect("Seleccione uno o más intervalos etarios", INTERVALOS_ETARIOS_EDUCACION, default="Todos")
    
    # Verificar si se seleccionó algún intervalo
    if st.button("Informar", key="nivel_mas_comun"):
        if not intervalo:
            st.warning("No se seleccionó un intervalo.")
            return
        
        # Si se selecciona "Todos", iterar por todos los intervalos disponibles
        if "Todos" in intervalo:
            intervalo = INTERVALOS_ETARIOS_EDUCACION  # Reemplazar "Todos" por todos los intervalos disponibles
        
        # Cargar los datos del DataFrame
        df = cargar_datos_ind()
        
        # Verificar si hay datos en los CSV cargados
        if df.empty:
            st.warning("No hay datos cargados.")
            return
        
        # Agrupar por nivel de estudio y edad, sumando la ponderación
        df = df.groupby(["CH12", "CH06"])["PONDERA"].sum().reset_index()
        
        resultados = []

        # Iterar por cada rango etario seleccionado
        for rango in intervalo:
            # Filtrar por el rango etario
            df_rango = agrupar_por_grupo_etario(df, [rango])
            
            # Verificar si hay datos después del filtrado
            if df_rango.empty:
                st.warning(f"No hay datos disponibles para el intervalo {rango}.")
                continue
            
            # Agrupar por nivel educativo y sumar la ponderación
            df_agrupado = df_rango.groupby("CH12")["PONDERA"].sum().reset_index()
            
            # Calcular el nivel educativo más común
            idx_max = df_agrupado["PONDERA"].idxmax()
            resultado = df_agrupado.loc[idx_max, "CH12"]
            
            # Guardar el rango y el nivel educativo más común
            resultados.append({"Rango Etario": rango, "Nivel Educativo": CH12_ID_A_NOMBRE[resultado]})
        
        # Crear el gráfico con Streamlit
        if resultados:
            # Convertir los resultados a un DataFrame
            df_resultados = pd.DataFrame(resultados)
            
            # Mostrar el gráfico de barras
            st.bar_chart(df_resultados.set_index("Rango Etario"))
def crear_csv_ranking():
    """Exporta el ranking de los 5 aglomerados a un archivo CSV.
    Retorna:
        str: Contenido del archivo CSV con el ranking de aglomerados.
    """
    ruta_csv_hogares =  PROJECT_PATH / "files_out" / "usu_hogares.csv"
    ruta_csv_individuos =  PROJECT_PATH / "files_out" / "usu_individuales.csv"
    ranking = ranking_aglomerados(ruta_csv_hogares, ruta_csv_individuos)
    
        #si  no hay datos en el ranking, mostrar un mensaje
    if ranking.empty:
        st.warning("No hay datos disponibles para generar el ranking.")
        return ""

        #convierto el ranking a csv
    return ranking.to_csv(index=False, encoding="utf-8")
        
        
def download_ranking_aglomerados():
    """Descarga el ranking de aglomerados con mayor porcentaje de hogares con 2 o más ocupantes con estudios universitarios o superiores finalizados.
    """
    #boton poara descargar el ranking
    if st.download_button(
            label="Descargar ranking de aglomerados",
            data=crear_csv_ranking(),
            file_name="ranking_aglomerados.csv",
            mime="text/csv"
        ):
        st.success("Ranking de aglomerados descargado exitosamente.")
def informar_no_hay_datos(df):
    """Informa si no hay datos en el DataFrame.
    
    Parámetros:
        df (pd.DataFrame): DataFrame a verificar.
    """
    if df.empty:
        st.warning("No hay datos disponibles par los archivos cargados.")
        return
     
def informar_incapaces_de_leer_escribir():
    """Informa el porcentaje de personas capaces e incapaces de leer y escribir mayores a 6 años año tras año .
    """
    if st.button("Informar capaces e incapaces de leer y escribir", key="incapaces_de_leer_escribir"):
        #cargar los datos del csv 
        df = cargar_datos_ind()
        #filtro por los mayores a 6 años
        df = df[df["CH06"] > 6]
        #filtro por los que no pueden leer ni escribir
        df_capaces = df[df["CH09"] == 1] 
        df_incapaces = df[df["CH09"] == 2]
        #agrupo por año y cuento la cantidad de personas
        df_agrupado_capaces = df_capaces.groupby("ANO4")["PONDERA"].sum().reset_index()
        df_agrupado_incapaces = df_incapaces.groupby("ANO4")["PONDERA"].sum().reset_index()
        #si no hay datos mostrar mensaje
        informar_no_hay_datos(df_agrupado_incapaces)
        informar_no_hay_datos(df_agrupado_capaces)
        #calculo el porcentaje de personas incapaces de leer y escribir
        df_agrupado_capaces["Porcentaje"] = (df_agrupado_capaces["PONDERA"] / df_agrupado_capaces["PONDERA"].sum()) * 100
        df_agrupado_incapaces["Porcentaje"] = (df_agrupado_incapaces["PONDERA"] / df_agrupado_incapaces["PONDERA"].sum()) * 100
        # Combinar ambos DataFrames para el gráfico
        df_combined = pd.DataFrame({
            "Año": df_agrupado_capaces["ANO4"],
            "Capaces": df_agrupado_capaces["Porcentaje"],
            "Incapaces": df_agrupado_incapaces["Porcentaje"]
        })

        # Mostrar el gráfico combinado
        st.subheader("Porcentaje de personas capaces e incapaces de leer y escribir por año")
        st.line_chart(df_combined.set_index("Año"))
        

    