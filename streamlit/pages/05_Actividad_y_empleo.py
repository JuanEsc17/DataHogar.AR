import streamlit as st
import sys
from pathlib import Path
from functions.functions_streamlit.functions_actividad_y_empleo import personas_desocupadas_estudios, tasa_desempleo_empleo, porcentajes_empleo, obtener_desempleo_empleo_mapa, mostrar_mapa
import pandas as pd
from utils.constantes import AGLOMERADO_ID_A_NOMBRE

sys.path.append(str(Path(__file__).resolve().parents[2] / 'src/'))

st.title("Actividad y empleo")

st.write("En esta sección podrás consultar información relacionada a la actividad y empleo de la población.")

st.divider()

# 1.5.1
st.subheader("Personas desocupadas por estudios alcanzados")
st.write("Informa la cantidad de personas desocupadas segun el nivel educativo alcanzado, para un año y trimestre determinados.")
anio = st.selectbox("Ingrese el año a informar", options=st.session_state["anios"])
trimestres = st.session_state['trimestres_por_año'].get(anio,[])
trimestre = st.selectbox("Ingrese el trimestre a informar", options=trimestres)
if st.button("Informar"):
    st.write(f"Resultados para el año {anio} y trimestre {trimestre}:")
    dic = personas_desocupadas_estudios(anio, trimestre)
    if not dic:
        st.warning("No se encontraron resultados para el año y trimestre ingresados.")
    else:
        st.bar_chart(dic, x_label='Nivel educativo', y_label='Cantidad de personas desocupadas', stack=False)
        with st.expander("🔍 Ver detalles del DataFrame"):
            st.dataframe(pd.DataFrame.from_dict(dic, orient='index', columns=['Cantidad']).reset_index().rename(columns={'index': 'Nivel educativo'}))

st.divider()
# 1.5.2 y 1.5.3
st.subheader("Evolución de la tasa de empleo y desempleo por aglomerado")
st.write("Informa la tasa de empleo y desempleo por aglomerado o todo el país, para todos los trimestres disponibles.")
aglomerados = [('Todo el país', '0')] + [(nombre, id_) for id_, nombre in AGLOMERADO_ID_A_NOMBRE.items()]
opcion = st.selectbox("Seleccione un aglomerado", aglomerados, format_func=lambda x:x[0], key="aglomerado")
if st.button("Informar grafico de empleo y desempleo"):
    resultado = tasa_desempleo_empleo(opcion[1])
    if resultado.empty:
        st.write("No se encontraron resultados para el aglomerado seleccionado.")
    else:
        st.line_chart(resultado.set_index('PERIODO')[['Tasa desempleo','Tasa empleo']], x_label='PERIODO', y_label='Tasa (%)')
        
st.divider()
# 1.5.4
st.subheader("Porcentajes de personas con cada tipo de empleo por aglomerado")
st.write("Informa el total de personas empleadas y el porcentaje de cada tipo de empleo (estatal, privado y otro)")
if st.button("Informar porcentajes de empleo"):
    resultado = porcentajes_empleo()
    st.bar_chart(resultado[['Empleo estatal', 'Empleo privado', 'Otro tipo']], x_label='AGLOMERADO', y_label='Porcentaje (%)', stack=False)
    st.dataframe(resultado[['Total']])

st.divider()
# 1.5.5
st.subheader("Mapa de empleo y desempleo por aglomerado")
st.write("Muestra un mapa interactivo según la tasa de empleo o desempleo.")
st.write("En caso de que seleccione 'Empleo' se mostrará con puntos verdes si la tasa de empleo creció, en rojo si decreció.")
st.write("En caso de que seleccione 'Desempleo' se mostrará con puntos verdes si la tasa de empleo decreció, en rojo si creció.")
eleccion = st.selectbox("Elija una opción", ["Empleo", "Desempleo"])
if st.button("Mostrar mapa"):
    resultado = obtener_desempleo_empleo_mapa(eleccion)
    mostrar_mapa(resultado)