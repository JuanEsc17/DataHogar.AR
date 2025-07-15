import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import altair as alt

from utils.constantes import DATA_OUT_PATH
from utils.constantes import AGLOMERADO_ID_A_NOMBRE
from functions.functions_comunes import validar_trimestre_disponible
#importo la constante con el path
archivo_ind = DATA_OUT_PATH / "usu_individuales.csv"
#INCISO 1.3.1
def generar_distribucion_edad_sexo(anio, trimestre):
    """
    Genera un gráfico de barras que muestra la distribución poblacional por grupo de edad y sexo
    para un año y trimestre específicos, usando datos de la EPH (Encuesta Permanente de Hogares).
    Parámetros: 
        año y trimestre.
    Retorna:
    fig : matplotlib.figure.Figure or None
        Gráfico de barras. Devuelve None si ocurre un error.
    mensaje_error : str or None
        Mensaje de error en caso de que ocurra algún problema (archivo no encontrado, columnas faltantes, etc.).
        Devuelve None si el gráfico se genera correctamente.
    Errores posibles:
    - Archivo CSV no encontrado o no se puede leer.
    - Faltan columnas requeridas en el archivo.
    - Año o trimestre no disponibles en los datos.
    - No hay datos luego del filtrado por año y trimestre.
    """
    # Leo el CSV
    try:
        df = pd.read_csv(archivo_ind, sep=';')
    except FileNotFoundError:
        return None, f"No se encontró el archivo: {archivo_ind}"
    except Exception as e:
        return None, f"Error al leer el archivo: {e}"

    # Validar columnas necesarias
    #CH06= edad; CH04: género; PONDERA: cantidad;
    columnas_necesarias = {'CH06', 'CH04_str', 'PONDERA', 'ANO4', 'TRIMESTRE'}
    if not columnas_necesarias.issubset(df.columns):
        return None, "Faltan columnas necesarias en el archivo."
    
    # Validar que el trimestre esté en los datos para ese año
    # No lo pide explícitamente pero como hay trimestres que pueden faltar lo agrego por las dudas
    es_valido, mensaje_error = validar_trimestre_disponible(df, anio, trimestre)
    if not es_valido:
        return None, mensaje_error
    
    # Filtrar por año y trimestre
    df_filtrado = df[(df["ANO4"] == anio) & (df["TRIMESTRE"] == trimestre)]

    if df_filtrado.empty:
        return None, "No hay datos para ese año y trimestre."
    
    # Ahora agrupo por grupo de edad en intervalos de 10 años
    df_filtrado["grupo_edad"] = pd.cut(      #pd.cut sirve para agrupar valores numéricos en intervalos 
        df_filtrado["CH06"],
        bins=list(range(0, 100, 10)) + [float("inf")],  #Esto crea los límites de los grupos, si es mas de 90 usa el inf
        right=False,
        labels=[f"{i}-{i+9}" for i in range(0, 90, 10)] + ["90+"]
        #labels es lo que luego se va a ver como grupo_edad en la tabla y el gráfico.
    )

    # Agrupo por edad y sexo con groupby (defino las columnas)
    # Con Pondera.sum estimo la poblacion total ya agrupada
    resumen = df_filtrado.groupby(["grupo_edad", "CH04_str"])["PONDERA"].sum().reset_index()
    # Reorganizo la tabla con pivot de manera que cada grupo de edad quede como una fila y cada sexo como una columna
    tabla = resumen.pivot(index="grupo_edad", columns="CH04_str", values="PONDERA").fillna(0)
    # Con fillna(0) reemplazo los valores nulos en caso de que los haya por 0

    # Crear gráfico
    # Con subplots creo una figura (fig) y un eje (ax) para graficar
    fig, ax = plt.subplots(figsize=(10, 6))
    # Tabla es mi DataFrame de pandas 
    # El método plot() de pandas se conecta internamente con matplotlib, indico que es un gráfico de barras
    tabla.plot(kind="bar", ax=ax)

    ax.set_title(f"Distribución por Edad y Sexo - {anio}T{trimestre}")
    ax.set_xlabel("Grupo de Edad")
    ax.set_ylabel("Población ponderada")
    ax.legend(title="Sexo")
    plt.xticks(rotation=45)
    # Formatear eje Y con separador de miles usando punto
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".")))
    
    return fig, None

#INCISO 1.3.2

#uso una tabla para mostrar los promedios
def edades_prom_por_aglomerado():
    """
    Calcula la edad promedio ponderada por aglomerado para el último año y trimestre disponibles
    en los datos de la Encuesta Permanente de Hogares (EPH).

    La función utiliza la variable `CH06` (edad) y el factor de expansión `PONDERA` para obtener
    un promedio representativo de la población real. El resultado es una tabla con el nombre del
    aglomerado y su edad promedio, ordenada de mayor a menor.

    Retorna: 
    pandas.DataFrame
        DataFrame con dos columnas:
        - "Aglomerado": nombre del aglomerado urbano.
        - "Edad promedio": edad promedio ponderada con dos decimales.
    """
    # Leo el CSV
    df_ind = pd.read_csv(archivo_ind, sep=';')
    # Uso el session state para obtener el ultimo trimestre y el ultimo año disponible
    ultimo_trimestre, ultimo_anio = st.session_state.tri_anio_max

    # Filtrar por último año y trimestre
    df_filtrado = df_ind[
        (df_ind["ANO4"] == ultimo_anio) & (df_ind["TRIMESTRE"] == ultimo_trimestre)
    ]
    # Calcular edad promedio ponderada por aglomerado
    df_resultado = (
        df_filtrado.groupby("AGLOMERADO") 
        .apply(lambda g: (g["CH06"] * g["PONDERA"]).sum() / g["PONDERA"].sum()) # apply me permite hacer una operación ponderada específica en cada grupo
        .reset_index(name="Edad promedio")
    )
    # Redondeo la edad prom para que solo queden 2 decimales
    df_resultado["Edad promedio"] = df_resultado["Edad promedio"].round(2)
    # Mapear nombres de aglomerado usando la funcion importada desde constantes
    df_resultado["Aglomerado"] = df_resultado["AGLOMERADO"].astype(str).map(AGLOMERADO_ID_A_NOMBRE)
    # Reordenar columnas de mayor a menor edad prom
    df_resultado = df_resultado[["Aglomerado", "Edad promedio"]].sort_values("Edad promedio", ascending=False)

    return df_resultado

# Inciso 1.3.3 : evolución de la dependencia demográfica

def calcular_dependencia_demografica_por_aglomerado(aglomerado_id):
    """
    Calcula la evolución del índice de dependencia demográfica para un aglomerado específico.
    Retorna un DataFrame con columnas: ['ANO4', 'TRIMESTRE', 'dependencia']
    """
    try:
        # Intentamos leer el archivo de datos (CSV separado por punto y coma)
        df = pd.read_csv(archivo_ind, sep=';')
    except FileNotFoundError:
        # Si el archivo no se encuentra, se devuelve un mensaje de error
        return None, f"No se encontró el archivo: {archivo_ind}"
    except Exception as e:
        # Para cualquier otro error al leer el archivo
        return None, f"Error al leer el archivo: {e}"

    # Verificamos que estén presentes las columnas necesarias
    columnas_necesarias = {'CH06', 'PONDERA', 'ANO4', 'TRIMESTRE', 'AGLOMERADO'}
    if not columnas_necesarias.issubset(df.columns):
        return None, "Faltan columnas necesarias en el archivo."

    # Filtramos el DataFrame para quedarnos solo con el aglomerado solicitado
    # Asegurarse que el aglomerado se compare como entero
    df = df[df["AGLOMERADO"] == int(aglomerado_id)]

    # Si no hay datos luego del filtro, se devuelve mensaje de error
    if df.empty:
        return None, "No hay datos para el aglomerado seleccionado."

    # Clasificar por grupo etario
    # 'dependiente' si tiene hasta 14 años o más de 64
    # 'activa' entre 15 y 64 años
    df['grupo_edad'] = pd.cut(
        df['CH06'], # Columna de edad
        bins=[-1, 14, 64, float('inf')],    # Columna de edad
        labels=['dependiente', 'activa', 'dependiente'],    # Etiquetas correspondientes
        ordered=False #con esta línea puedo repetir la label dependiente
    )

    # Agrupamos por año, trimestre y grupo de edad, y sumamos el peso muestral con pondera
    resumen = df.groupby(['ANO4', 'TRIMESTRE', 'grupo_edad'])['PONDERA'].sum().reset_index()
    # Reorganizamos el DataFrame para tener una columna por grupo etario
    pivot = resumen.pivot(index=['ANO4', 'TRIMESTRE'], columns='grupo_edad', values='PONDERA').fillna(0)
    
    # Calculamos el índice de dependencia demográfica: (dependientes / activos) * 100
    pivot['dependencia'] = (pivot['dependiente'] / pivot['activa']) * 100
    pivot['dependencia'] = pivot['dependencia'].round(2) #para que queden solo 2 decimales
    # Calculamos el índice de dependencia demográfica: (dependientes / activos) * 100
    pivot = pivot.reset_index()

    return pivot, None  # Devolvemos el DataFrame resultante y sin errores

def generar_grafico_dependencia(df_dependencia: pd.DataFrame):
    """
    Genera un gráfico de línea de Altair con la evolución de la dependencia demográfica.
    Recibe un DataFrame con columnas 'Año', 'Trimestre' y 'dependencia'.
    """
    # Eliminamos filas con valores nulos en la columna 'dependencia'
    # Si no aparecía el trimestre 4 de 2024 con None
    df = df_dependencia.dropna(subset=["dependencia"]).copy()

    # Si luego de eliminar nulos el DataFrame queda vacío, no generamos gráfico
    if df.empty:
        return None  

    # Creamos una nueva columna combinando año y trimestre, por ejemplo: "2024T2"
    df["periodo"] = df["Año"].astype(str) + "T" + df["Trimestre"].astype(str)

    # Definimos límites del eje Y ajustados a los valores mínimos y máximos de dependencia
    # Si no el gráfico no quedaba en escala, se veía muy chico y no era representativo
    ymin = df["dependencia"].min() - 0.5
    ymax = df["dependencia"].max() + 0.5

    # Creamos el gráfico con Altair: línea con puntos y tooltip
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X("periodo", title="Periodo", sort=None), # Eje X: períodos
        y=alt.Y("dependencia", title="Dependencia Demográfica", scale=alt.Scale(domain=[ymin, ymax])),  # Eje Y
        tooltip=["periodo", "dependencia"]  # Información al pasar el mouse
    ).properties(
        width="container",  # Ancho automático
        height=400,         # Ajustamos la altura
        title="Evolución de la Dependencia Demográfica"
    )

    return chart    # Devolvemos el gráfico generado

#Inciso 1.3.4: Informar para cada año la media y la mediana de la edad de la poblacion:
def media_y_mediana_edad_por_periodo() -> pd.DataFrame:
    """
    Calcula la media y mediana de la edad de la población para cada año y trimestre.

    Retorna:
        Gráfico de barras.
    """
    # Cargamos el archivo CSV
    df = pd.read_csv(archivo_ind, sep=';')

    # Eliminamos filas con edad nula
    df = df.dropna(subset=["CH06", "ANO4", "TRIMESTRE"])

    # Agrupamos por año y trimestre
    resumen = df.groupby(["ANO4", "TRIMESTRE"]).apply(
        # Para cada grupo (año + trimestre), calculamos:
        lambda grupo: pd.Series({
            # La edad media ponderada: sumamos edad * ponderador y dividimos por la suma de ponderadores
            # Redondeamos el resultado a un decimal
            "Edad media": round((grupo["CH06"] * grupo["PONDERA"]).sum() / grupo["PONDERA"].sum(), 1),
            # La edad mediana: usamos repetición de filas según el peso poblacional (PONDERA)
            # Esto simula una mediana ponderada expandiendo la muestra
            "Edad mediana": grupo.loc[grupo.index.repeat(grupo["PONDERA"].round().astype(int)), "CH06"].median()
        })
    ).reset_index() # Restablecemos el índice para tener un DataFrame normal

    # Crear columna de período tipo "2023T1"
    resumen["Periodo"] = resumen["ANO4"].astype(str) + "T" + resumen["TRIMESTRE"].astype(str)
    # Datos para el gráfico
    periodos = resumen["Periodo"]
    medias = resumen["Edad media"]
    medianas = resumen["Edad mediana"]

    # A partir de aca: diseño del gráfico
    # Tamaño del gráfico
    fig, ax = plt.subplots(figsize=(12, 6))
    # Posiciones de las barras
    x = range(len(periodos))
    ancho = 0.35
    # Barras
    ax.bar([i - ancho/2 for i in x], medias, width=ancho, label='Media', color='green')
    ax.bar([i + ancho/2 for i in x], medianas, width=ancho, label='Mediana', color='pink')
    
    # Ejes y leyenda
    ax.set_xlabel("Periodo")
    ax.set_ylabel("Edad (años)")
    ax.set_title("Edad media y mediana por trimestre")
    ax.set_xticks(x)
    ax.set_xticklabels(periodos, rotation=45)
    ax.legend()

    # Ajusta automáticamente los márgenes del gráfico para que se vea ordenado
    plt.tight_layout()
    return fig