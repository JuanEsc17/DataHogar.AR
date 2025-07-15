import streamlit as st
from pathlib import Path
import sys
import altair as alt #es para el grafico que no se si voy a usar


sys.path.append(str(Path(__file__).resolve().parents[2] / 'src'))
from functions.functions_streamlit.functions_caracteristicas_demo import generar_distribucion_edad_sexo
from functions.functions_streamlit.functions_caracteristicas_demo import edades_prom_por_aglomerado
from utils.constantes import AGLOMERADO_ID_A_NOMBRE
from functions.functions_streamlit.functions_caracteristicas_demo import calcular_dependencia_demografica_por_aglomerado
from functions.functions_streamlit.functions_caracteristicas_demo import generar_grafico_dependencia
from functions.functions_streamlit.functions_caracteristicas_demo import media_y_mediana_edad_por_periodo

st.title("Distribución por Edad y Sexo")

#Inciso 1.3.1
# Le solicito al usuario que seleccione el año 
anio = st.selectbox("Seleccioná el año:", options=st.session_state["anios"])

trimestre = st.selectbox("Seleccione el trimestre", [1, 2, 3, 4])


if st.button("Generar gráfico"):
    fig, error = generar_distribucion_edad_sexo(anio, trimestre)
    if error:
        st.error(error)
    else:
        st.pyplot(fig)

st.title("Edad promedio por aglomerado")
st.subheader("Datos del último trimestre disponible")
tabla_edad_prom = edades_prom_por_aglomerado()

# Mostrar en tabla
st.dataframe(tabla_edad_prom, use_container_width=True)


# Inciso 1.3.3 : dependencia demográfica
st.title("Evolución de la Dependencia Demográfica")
st.subheader("La dependencia demográfica se define como el cociente entre población población de 0 a 14 años y mayores de 65 respecto a la población en edad activa")

# Selector de aglomerado
# Creamos un diccionario que mapea el nombre del aglomerado al ID correspondiente
nombre_a_id_aglomerado = {v: k for k, v in AGLOMERADO_ID_A_NOMBRE.items()}
# Mostramos un selector (dropdown) en Streamlit para elegir un aglomerado
nombre_aglomerado = st.selectbox("Seleccione un aglomerado", list(nombre_a_id_aglomerado.keys()))
# Obtenemos el ID del aglomerado seleccionado (como string)
aglomerado_id = nombre_a_id_aglomerado[nombre_aglomerado]  # sigue siendo str

# Calculamos el índice de dependencia demográfica para el aglomerado seleccionado
df_dependencia, error = calcular_dependencia_demografica_por_aglomerado(aglomerado_id)

if error:
    # Si hubo un error al calcular, lo mostramos
    st.error(error)
# Si no hubo error y tenemos datos:
elif df_dependencia is not None:
    # Renombramos las columnas para que se vean mejor en el gráfico y la tabla
    df_dependencia = df_dependencia.rename(columns={'ANO4': 'Año', 'TRIMESTRE': 'Trimestre'})

    # Generamos el gráfico de líneas usando la función importada
    chart = generar_grafico_dependencia(df_dependencia)
    # Mostramos el gráfico en Streamlit
    st.altair_chart(chart, use_container_width=True)

    # Mostrar tabla debajo
    # Eliminamos filas con datos nulos
    df_dependencia = df_dependencia.dropna(subset=["dependencia"])
    st.dataframe(df_dependencia[["Año", "Trimestre", "dependencia"]], use_container_width=True, hide_index=True)
    

#Inciso 1.3.4: mostrar la media y mediana de la población

st.title("Media y mediana de edad por período")
# Breve descripción de los conceptos:
st.write("Media: promedio de un conjunto de números, se calcula sumando todos los números y dividiendo el resultado por la cantidad de números.")
st.write("Mediana:  es el valor central de un conjunto de datos ordenados.")
# Obtenemos los datos
df_edad = media_y_mediana_edad_por_periodo()


# Mostramos el gráfico de barras
fig = media_y_mediana_edad_por_periodo()
st.pyplot(fig)
