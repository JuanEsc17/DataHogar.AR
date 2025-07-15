import streamlit as st
from pathlib import Path
import pandas as pd
from utils.constantes import DATA_PATH, DATA_OUT_PATH
from functions.functions_comunes import obtener_primer_trimestre_y_anio, obtener_ultimo_trimestre_y_anio

# Cargar datasets
canasta_path = DATA_PATH / "valores-canasta-basica-alimentos-canasta-basica-total-mensual-2016.csv"
hogares_path = DATA_OUT_PATH / "usu_hogares.csv"
df_canasta = pd.read_csv(canasta_path, delimiter=",")
df_hogares = pd.read_csv(hogares_path, delimiter=";")

st.title("Ingresos")
st.subheader("Calcular hogares por debajo de la línea de pobreza e indigencia (último mes del trimestre)")


anios = st.session_state['trimestres_por_año'].keys()
anio = st.selectbox("Elige un año:", anios)
trimestres = st.session_state['trimestres_por_año'].get(anio,[])
trimestre = st.selectbox("Elige un trimestre (último mes):", trimestres )
mes = trimestre * 3

# filtro por año y mes
canasta_filtrada = df_canasta[
    (df_canasta["indice_tiempo"].str.startswith(f"{anio}-")) &
    (df_canasta["indice_tiempo"].str[5:7] == f"{mes:02d}")
]

if canasta_filtrada.empty:
    st.error("No se encontraron datos de canasta para el período seleccionado.")
else:
    # tomo la primera fila de la linea de pobreza e indigencia
    linea_indigencia = canasta_filtrada["linea_indigencia"].iloc[0]
    linea_pobreza = canasta_filtrada["linea_pobreza"].iloc[0]

    # Filtrar hogares: solo aquellos con 4 integrantes y que correspondan al año y trimestre indicado.
    hogares_de_4_filtrado = df_hogares[
        (df_hogares["IX_TOT"] == 4) &
        (df_hogares["ANO4"] == anio) &
        (df_hogares["TRIMESTRE"] == trimestre)
    ]

    if hogares_de_4_filtrado.empty:
        st.error("No se encontraron hogares con 4 integrantes para el período seleccionado.")
    else:
        # Condiciones para evaluar el ingreso total del hogar (ITF)
        # Pobreza: ITF menor a la línea de pobreza, pero mayor o igual a la de indigencia
        condicion_pobreza = (
            (hogares_de_4_filtrado["ITF"] < linea_pobreza) &
            (hogares_de_4_filtrado["ITF"] >= linea_indigencia)
        )
        # Indigencia: ITF menor a la línea de indigencia
        condicion_indigencia = (hogares_de_4_filtrado["ITF"] < linea_indigencia)

        # Se suma la columna de ponderación para informar resultados ponderados
        total = sum(hogares_de_4_filtrado["PONDERA"])
        pobreza_tot = sum(hogares_de_4_filtrado.loc[condicion_pobreza, "PONDERA"])
        indigencia_tot = sum(hogares_de_4_filtrado.loc[condicion_indigencia, "PONDERA"])

        if st.button("Informar"):
            st.write(f"Total ponderado de hogares: {total:,.0f}")
            st.write(f"Hogares por debajo de la línea de pobreza: {pobreza_tot:,.0f} "
                     f"({(linea_pobreza/total)*100:.2f}%)")
            st.write(f"Hogares por debajo de la línea de indigencia: {indigencia_tot:,.0f} "
                     f"({(indigencia_tot/total)*100:.2f}%)")
