import streamlit as st
from pathlib import Path
import sys
from utils.constantes import PROJECT_PATH
from utils.constantes import DATA_OUT_PATH
from utils.constantes import DATA_PATH
from utils.constantes import INPUT_PATTERN_HOGARES
from utils.constantes import INPUT_PATTERN_INDIVIDUOS
from utils.constantes import OUTPUT_FILENAME_HOGARES
from utils.constantes import OUTPUT_FILENAME_INDIVIDUOS


# Agregar 'src' al path
sys.path.append(str(PROJECT_PATH / 'src'))

# Importo la funcion que transforma los files para agregar archivos nuevos
# Esta funcion es la que me va a servir para actualizar el dataset con el boton
from functions.functions_A import transform_files, apply_changes_hogares, apply_changes_individuos

# Importo la funcion para el inciso 1.2:
from functions.functions_streamlit.functions_carga_datos import chequeo_archivos_por_contenido



st.sidebar.header("Carga de datos")
st.title("Carga de datos")

#importar una funcion para obtener primer y ultimo trimeste disp
#primera parte: imprimir primer y ultimo trimestre con las funciones de los puntos 1 y 2:


input_folder = DATA_PATH
output_folder = DATA_OUT_PATH


file_path_personas = output_folder/ OUTPUT_FILENAME_INDIVIDUOS
file_path_hogares = output_folder/ OUTPUT_FILENAME_HOGARES

trimestre_min, anio_min = st.session_state.tri_anio_min
trimestre_max, anio_max = st.session_state.tri_anio_max


st.write(
    "El sistema contiene informacion desde el trimestre {} de {} hasta el trimestre {} del año {}".format(trimestre_min,anio_min,trimestre_max,anio_max)
    )

#Segunda parte: tengo que realizar una funcion para actualizar el dataset con el click del boton
#tengo que actualizar la carpeta files, tanto files in como files out
# creo el path a la carpeta con archivos .txt descargados

# Esta función se ejecutará al hacer clic en el botón
def actualizar_dataset():
    try:
        transform_files(INPUT_PATTERN_INDIVIDUOS ,input_folder,OUTPUT_FILENAME_INDIVIDUOS ,apply_changes_individuos) 
        transform_files(INPUT_PATTERN_HOGARES,input_folder,OUTPUT_FILENAME_HOGARES ,apply_changes_hogares)
        
        st.success("¡Dataset actualizado correctamente!")
    except Exception as e:
        st.error(f"Error: {e}")

st.button('Actualizar DataSet', on_click=actualizar_dataset)
#en el on_click = nuestra funcion para actualizar data

# Segunda parte del trabajo inciso 1.2: 
# Proceso que controle que para cada archivo de invividuos exista uno de hogares y viceversa:
#aca solo voy a llamar a la funcion de functions carga de datos.


st.title("Chequeo de archivos EPH")
#uso un boton para ejecutar mi funcion:
if st.button("Ejecutar chequeo de archivos"):
    #asigno mi funcion importada a una variable y la paso el path a los files por parametro
    faltantes = chequeo_archivos_por_contenido(input_folder)

    if faltantes:
        #si se encuentra algún fantante se muestra un cartel de warning
        st.warning("Se encontraron inconsistencias:")
        for anio, trimestre, tipo in faltantes:
            st.write(f"Falta archivo de {tipo} para Año: {anio}, Trimestre: {trimestre}")
    else:
        st.success("Chequeo exitoso. No se encontraron inconsistencias.")