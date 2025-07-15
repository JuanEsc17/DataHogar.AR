import streamlit as st
from pathlib import Path
import matplotlib.pyplot as plt
import sys
sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))
from functions.functions_streamlit.functions_educacion import grafico_maximo_nivel_educativo_alcanzado, informar_nivel_mas_comun, download_ranking_aglomerados, informar_incapaces_de_leer_escribir
st.title("Educación")
st.write("En esta sección se visualizará información relacionada al nivel de educación alcanzado por la población argentina según la EPH.")
st.divider()


st.write("A continuación se presenta un gráfico de barras que muestra el máximo nivel educativo alcanzado por los encuestados en el año seleccionado.")
grafico_maximo_nivel_educativo_alcanzado()
st.divider()
st.write("Visualizacion de intervalo etario de nivel educacional alcanzado más común")
informar_nivel_mas_comun()
st.divider()
st.write("Exportar ranking de 5 aglomerados con mayor porcentaje de hogares con 2 o mas ocupantes con estudios universitarios o superiores finalzados")
download_ranking_aglomerados()
st.divider()
st.write("Informar porcentaje de personas capaces e incapaces de leer y escribir mayores a 6 años por año")
informar_incapaces_de_leer_escribir()
