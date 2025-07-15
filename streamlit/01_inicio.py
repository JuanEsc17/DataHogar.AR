import streamlit as st
from pathlib import Path
import sys
import pandas as pd
sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))

from utils.constantes import PROJECT_PATH
from functions.functions_B import  obtener_ultimo_trimestre_y_anio
from functions.functions_st import obtener_primer_trimestre_y_anio
from functions.functions_comunes import obtener_primer_trimestre_y_anio
folder_path = Path(__file__).resolve().parents[1] / 'files_out'

file_path_personas = folder_path/ "usu_individuales.csv"
file_path_hogares = folder_path/ "usu_hogares.csv"

st.session_state["tri_anio_min"] = obtener_primer_trimestre_y_anio(file_path_hogares, file_path_personas)
st.session_state["tri_anio_max"] = obtener_ultimo_trimestre_y_anio(file_path_hogares, file_path_personas)
# Guardamos los años disponibles para poder reutilizarlos en las distintas páginas
st.session_state["anios"] = list(range(st.session_state.tri_anio_min[1],st.session_state.tri_anio_max[1] + 1))

# generacion de diccionario de trimestres por año
df_hogares = pd.read_csv(file_path_hogares,sep=";",usecols=["ANO4","TRIMESTRE"])
diccionario_trimestres = {año: list(trimestres) for año, trimestres in df_hogares.groupby("ANO4")["TRIMESTRE"].unique().items()}
# asignando diccionario al session state
if 'trimestres_por_año' not in st.session_state:
    st.session_state['trimestres_por_año'] = diccionario_trimestres

#Titulo de la aplicacion
st.title("DataHogar.AR")
st.divider()

#Descripcion de la aplicacion
st.write("Desarrollamos herramientas en Python para el procesamiento y enriquecimiento de los microdatos de las Encuestas Permanentes de Hogares (EPH) de Argentina. Nuestro trabajo consiste en agregar nuevas variables calculadas, transformar y limpiar datos existentes, y generar archivos actualizados y listos para su análisis. El objetivo es facilitar el acceso a información social y económica de calidad, optimizada para investigaciones, visualizaciones y toma de decisiones. ")
st.divider()

#Defino las rutas de las paginas
pages_path = PROJECT_PATH / 'streamlit' / 'pages'
carga_de_datos_path = pages_path/'02_Carga_de_datos.py'
caracteristicas_demograficas_path = pages_path/'03_Características_demográficas.py'
caracteristicas_de_la_vivienda_path = pages_path/'04_Características_de_la_vivienda.py'
actividad_y_empleo_path = pages_path/'05_Actividad_y_empleo.py'
educacion_path = pages_path/'06_Educación.py'
ingresos_path = pages_path/'07_Ingresos.py'

st.page_link(carga_de_datos_path, label='Ir a carga de datos', icon='📊')

st.page_link(caracteristicas_demograficas_path, label='Ir a Características demográficas', icon='🔍')
st.page_link(caracteristicas_de_la_vivienda_path, label='Ir a Caraterísticas de la vivienda', icon='📈')
st.page_link(actividad_y_empleo_path, label= 'Ir a Actividad y empleo', icon='💼')
st.page_link(educacion_path, label= 'Ir a Educación', icon='📚')
st.page_link(ingresos_path, label= 'Ir a Ingresos', icon='💸')