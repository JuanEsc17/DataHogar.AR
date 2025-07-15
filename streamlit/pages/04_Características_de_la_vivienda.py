from pathlib import Path
import sys
from functions.functions_streamlit.functions_vivienda import filtrar_por_anio_ingresado, grafico_barras_banio, obtener_disponen_banio, obtener_evolucion_tenencia, obtener_material_predominante, pie_chart, porcentaje_por_tipo_de_vivienda, obtener_cant_villa_de_emergencia, obtener_porcentaje_condicion_habitabilidad
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from utils.constantes import AGLOMERADO_ID_A_NOMBRE, DATA_OUT_PATH, TENENCIA_ID_A_NOMBRE
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

archivo_hogares = DATA_OUT_PATH / "usu_hogares.csv"
archivo_individuos = DATA_OUT_PATH / "usu_individuales.csv"
df_hogares = pd.read_csv(archivo_hogares, sep=";")
df_individuos = pd.read_csv(archivo_individuos, sep=";")

opciones_anios = list(st.session_state["anios"]) 
opciones_anios.append("Todos los años")

st.title("📈Características de la vivienda")
st.subheader("En esta sección se visualizará información relacionada a las características de las viviendas de la población argentina según la Encuesta Permanente de Hogares")
option = st.selectbox("Seleccioná el año para filtrar", opciones_anios)
# Filtramos por Año según lo ingresado por el Usuario y SIN repetidos con CODUSU.
hogares_filtrados = filtrar_por_anio_ingresado(df_hogares,option)
individuos_filtrados = filtrar_por_anio_ingresado(df_individuos,option)

# Inciso 1.4.1
cantidad_de_viviendas = hogares_filtrados["PONDERA"].sum()
st.subheader("Cantidad total ponderada de viviendas")
st.write(f"Se muestra la cantidad total de viviendas incluidas en la encuesta para el año:", option)
st.write(f"📊Cantidad de viviendas: {cantidad_de_viviendas:,.0f}") 
# st.metric(label="Viviendas totales:", value=f"{cantidad_de_viviendas:,.0f}")

#Inciso 1.4.2
st.divider()
st.subheader("Proporción de viviendas según su tipo")
st.write("Se presentará un gráfico de torta (pie chart) con la proporción de viviendas según su tipo para el año:", option)
if st.button("Mostrar gráfico de torta"):
    proporcion_viviendas_segun_tipo = porcentaje_por_tipo_de_vivienda(hogares_filtrados,cantidad_de_viviendas)
    grafico_pie_chart = pie_chart(proporcion_viviendas_segun_tipo)

# Inciso 1.4.3
st.divider()
st.subheader("Material predominante en los pisos interiores según Aglomerado:")
st.write("Informa para cada aglomerado, cuál es el material predominante en los pisos interiores de las viviendas para el año:", option)
if st.button("Informar material predominante por Aglomerado"):
    material_predominante = obtener_material_predominante(hogares_filtrados)
    material_predominante = material_predominante.reset_index(drop=True)
    st.dataframe(material_predominante)

# Inciso 1.4.4
st.divider()
st.subheader("Viviendas que disponen de baño dentro del hogar por Aglomerado")
st.write("Muestra por aglomerado, la proporción de viviendas que disponen de baño dentro del hogar para el año:", option)
if st.button("Mostrar la proporción de viviendas con baño dentro del hogar"):
    proporcion_de_viviendas_con_banio = obtener_disponen_banio(hogares_filtrados)
    proporcion_de_viviendas_con_banio["Porcentaje"] = proporcion_de_viviendas_con_banio["Porcentaje"].round(2)
    fig = grafico_barras_banio(proporcion_de_viviendas_con_banio)
    st.pyplot(fig)

# Inciso 1.4.5
st.divider()
st.subheader("Evolución del Régimen de Tenencia")
st.write("Se mostrará la evolución del régimen de tenencia para el aglomerado seleccionado", option)
aglomerados_nombres = sorted(AGLOMERADO_ID_A_NOMBRE.values())
option_aglomerados = st.selectbox(
    "Seleccioná el aglomerado para filtrar",
    (aglomerados_nombres),
)
# Mostrar mensaje
st.markdown(f"🔍 **Aglomerado seleccionado:** `{option_aglomerados}`")
with st.expander("📊 Filtrar por régimen de tenencia"):
    tenencia_options = list(TENENCIA_ID_A_NOMBRE.values())
    option_tenencias = st.multiselect(
        "Seleccioná el/los régimen/es de tenencia que querés analizar",
        tenencia_options,
        default=tenencia_options
    )

# Botón para mostrar gráfico
if st.button("Mostrar gráfico de evolución de la tenencia"):
    obtener_evolucion_tenencia(hogares_filtrados, option_aglomerados, option_tenencias)

# Inciso 1.4.6
st.divider()
st.subheader("Viviendas ubicadas en villa de emergencia")
st.write("Se mostrará la cantidad y porcentaje de viviendas ubicadas en villa de emergencia por aglomerado para el año:",option)

df_viillas_emergencia = obtener_cant_villa_de_emergencia(hogares_filtrados)

# conserva el orden de los aglomerados
df_viillas_emergencia["Aglomerado"] = pd.Categorical(
    df_viillas_emergencia["Aglomerado"],
    categories=df_viillas_emergencia["Aglomerado"],
    ordered=True
)
if st.button("Mostrar gráfico de cantidad de villas de emergencia"):
    # creo el grafico de barras definiendo eje x (Aglomerado) e y (cantidad de villas de emergencia)
    st.bar_chart(df_viillas_emergencia.set_index("Aglomerado")["VillasEmergencia"])
    st.markdown("### Porcentajes por Aglomerado")

    # itero sobre df para crear markdowns que especifiquen el porcentaje
    for idx, row in df_viillas_emergencia.iterrows():
        st.markdown(f"- **{row["Aglomerado"]}**: {row["Porcentaje"]}")


# Inciso 1.4.7
st.divider()
st.subheader("Viviendas por condicion de habitabilidad")
st.write("Se mostrará la cantidad de viviendas segun su condicion de habitabilidad por aglomerado para el año:",option)

df_condicion_hogares = obtener_porcentaje_condicion_habitabilidad(hogares_filtrados)
if st.button("Mostrar tabla de condicion de hogares"):
    st.dataframe(df_condicion_hogares)

# Convertir a CSV
csv = df_condicion_hogares.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Descargar CSV",
    data=csv,
    file_name="resultados_habitabilidad.csv",
    mime="text/csv"
)