from matplotlib import pyplot as plt
import pandas as pd
import streamlit as st
from utils.constantes import AGLOMERADO_ID_A_NOMBRE, PISO_ID_A_NOMBRE, TENENCIA_ID_A_NOMBRE, VIVIENDAS_ID_A_NOMBRE

# Inciso 1.4.1
def filtrar_por_anio_ingresado(df_hogares, anio_ingresado):
    """ Filtra el DataFrame de hogares según el año ingresado y elimina duplicados por CODUSU.
    Args:
        df_hogares (pd.DataFrame): DataFrame que contiene los datos de hogares, con la columna "ANO4".
        anio_ingresado: Año a filtrar (por ejemplo, "2022"). Si se pasa "Todos los años", no se aplica filtro.
    Returns:
        pd.DataFrame: DataFrame filtrado por año (si corresponde), sin duplicados en la columna "CODUSU".
    """
    if anio_ingresado == "Todos los años":
        df_filtrado = df_hogares
    else:
        df_filtrado = df_hogares[df_hogares["ANO4"] == anio_ingresado]
    # Devolvemos aquellos que NO estén duplicados.
    return df_filtrado.drop_duplicates(subset="CODUSU")

# Inciso 1.4.2
def contar_tipos_vivienda(df_hogares):
    """
    Cuenta la cantidad de hogares según el tipo de vivienda.
    Convierte la columna "IV1" a numérica para poder filtrar correctamente, luego suma
    los valores para cada tipo de vivienda según los códigos de "IV1".
    Args:
        df_hogares (pd.DataFrame): DataFrame que contiene los datos de hogares.
    Returns:
        dict: Diccionario con las claves siendo los nombres de tipos de vivienda y los valores la suma ponderada correspondiente a cada tipo.
        Ejemplo: {"Casa": 1234, "Departamento": 500, ...}
    """
    # Nos aseguramos que el valor de IV1 esté en valor numérico para poder hacer las comparaciones
    df_hogares["IV1"] = pd.to_numeric(df_hogares["IV1"], errors="coerce")
    # Creamos un tipo de diccionario conteo, eso es para que por CLAVE con el tipo de vivienda, nos guarde como valor
    # La cantidad PONDERADA que hay de ese tipo. Es decir, {Casa: 1234, Depto: 500, Pieza: 100} y así sucesivamente.
    conteo = (
    df_hogares[df_hogares["IV1"].isin(VIVIENDAS_ID_A_NOMBRE.keys())].groupby("IV1")["PONDERA"].sum().rename(index=VIVIENDAS_ID_A_NOMBRE).to_dict())
    return conteo


def porcentaje_por_tipo_de_vivienda(df_hogares, cantidad_de_viviendas):
    """
    Calcula el porcentaje que representa cada tipo de vivienda respecto al total de viviendas.
    Utiliza la función `contar_tipos_vivienda` para obtener la cantidad de viviendas
    por tipo, y luego calcula el porcentaje de cada tipo.
    Args:
        df_hogares (pd.DataFrame): DataFrame con los datos de hogares.
        cantidad_de_viviendas (float o int): Cantidad total de viviendas sobre la cual se calcularán los porcentajes.
    Returns:
        dict: Diccionario donde las claves son los tipos de vivienda y los valores son los porcentajes correspondientes.
        Por ejemplo: {"Casa": 33.5, "Departamento": 22.1, ...}
    """
    contar_viviendas_segun_tipo = contar_tipos_vivienda(df_hogares)
# Sacamos el porcentaje de cada tipo de vivienda. {Casa: 33%, Depto: 22% } y así sucesivamente.
    porcentaje_tipo_viviendas = {}
    for tipo, cantidad in contar_viviendas_segun_tipo.items():
        if cantidad_de_viviendas > 0:
            porcentaje = (cantidad / cantidad_de_viviendas) * 100
        else:
            porcentaje = 0
        porcentaje_tipo_viviendas[tipo] = porcentaje
    return porcentaje_tipo_viviendas

# Función para el grafico
def autopct_func(porcentaje):
    if porcentaje >= 3:
        return f"{porcentaje:.1f}%"
    else:
        return ""

def pie_chart(proporcion_viviendas_segun_tipo):
    # Nombres del tipo de vivienda
    labels = list(proporcion_viviendas_segun_tipo.keys())
    # El tamaño de cada porción de la torta, por eso values del diccionario
    sizes = list(proporcion_viviendas_segun_tipo.values())
    # Crea una figura de Matplotlib de tamaño 8x6 con un sólo eje, "ax"
    # que es dónde se va dibujar el gráfico.
    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        # Sizes define el tamaño de cada porción
        sizes,
        # Las labels las sacamos del gráfico, las tenemos aparte
        labels=None,
        # Sólo mostramos los porcentajes de cada tipo de vivienda si superan el 3%
        autopct=lambda pct: autopct_func(pct),
        shadow=True,
        # El color del texto se ve blanco
        textprops=dict(color="white")
    )
    # Esto es el cuadro que muestra los labels al costado
    # Lo ubica a la izquierda (o sea por fuera del gráfico) usando bbox_to_anchor
    ax.legend(
        wedges,
        labels,
        title="Tipo de vivienda",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1)
    )

    ax.set_title("Distribución de tipos de vivienda")
    # Para que el gráfico sea circular y no ovalado.
    ax.axis("equal")

    st.pyplot(fig)

# Inciso 1.4.3
def obtener_material_predominante(df_hogares):
    """
    Obtiene el material predominante en los pisos interiores para cada aglomerado.
    Agrupa los datos por "AGLOMERADO" y "IV3" (tipo de piso), sumando la ponderación para cada grupo.
    Para cada aglomerado, selecciona el tipo de piso con la mayor ponderación (el material predominante).
    Finalmente, reemplaza los códigos numéricos su nombre.
    Args:
        df_hogares (pd.DataFrame): DataFrame que contiene los datos de hogares.
    Returns:
        pd.DataFrame: DataFrame con columnas "Aglomerado" y "Material de piso", donde cada fila corresponde 
        a un aglomerado y su material de piso predominante.
    """
    # Nos aseguramos que el valor de IV3 esté en valor numérico para poder hacer las comparaciones
    df_hogares["IV3"] = pd.to_numeric(df_hogares["IV3"], errors="coerce")

    # Agrupamos por aglomerado y tipo de piso. El groupby lo que hace es agrupar el DataFrame por AGLOMERADO y IV3.
    # Esto se vería como: AGLOMERADO: 33, IV3:1, PONDERA: 10, AGLOMERADO 33, IV3:2,PONDERA:15 -> TABLA.
    # Luego se suman con el .sum(). 
    # Si reiciamos usando .reset_index() hace que las columnas se vuelvan al DataFrame normal y se vean como una TABLA.
    conteo_ponderado = df_hogares.groupby(["AGLOMERADO", "IV3"])["PONDERA"].sum().reset_index()

    # conteo_ponderado es un DataFrame con la estructura tipo tabla que tiene Aglomerado, tipo de piso y la cantidad ponderada de ese tipo.
    # Lo que hacemos ahora es a ese DataFrame con loc buscar el índice en dónde pondera es más alto.
    # Es decir, sacamos el máximo de los valores a partir de la fila. Obtiene el "id/fila" más grande.  
    material_predominante = conteo_ponderado.loc[conteo_ponderado.groupby("AGLOMERADO")["PONDERA"].idxmax()]
    # Sólo para que se vea mejor, reemplazamos a lo que se encuentra en IV3  (un número) a un string.
    material_predominante["Material de piso"] = material_predominante["IV3"].replace(PISO_ID_A_NOMBRE)
    material_predominante["Aglomerado"] = material_predominante["AGLOMERADO"].astype(str).replace(AGLOMERADO_ID_A_NOMBRE)
    # Devuelve dataframe
    return material_predominante[["Aglomerado", "Material de piso"]]

# Inciso 1.4.4
def obtener_disponen_banio(df_hogares):
    """
    Calcula el porcentaje de viviendas que disponen de baño para cada aglomerado.
    Calcula el total ponderado de viviendas por aglomerado y la suma de viviendas que tienen baño (donde "IV9" == 1) por aglomerado.
    Finalmente, calcula el porcentaje de viviendas con baño respecto al total de viviendas
    en cada aglomerado.
    Args:
        df_hogares (pd.DataFrame): DataFrame que contiene datos de hogares.
    Returns:
        pd.DataFrame: DataFrame con columnas "Aglomerado" y "Porcentaje", donde cada fila representa 
        un aglomerado y el porcentaje ponderado de viviendas que disponen de baño.
    """
    # Nos aseguramos que el valor de IV3 esté en valor numérico para poder hacer las comparaciones
    df_hogares["IV9"] = pd.to_numeric(df_hogares["IV9"], errors="coerce")
    # Agrupamos por aglomerado. El groupby lo que hace es agrupar el DataFrame por AGLOMERADO y IV9.
    # Una vez agrupado, por ese grupo se guarda la PONDERACIÓN. Esto por ahora es una Serie 
    # Como índice tenemos los Aglomerados. Como valor, tenemos la suma de la ponderación.
    # Si reiciamos usando .reset_index() hace que las columnas se vuelvan al DataFrame normal y se vean como una TABLA.
    total_ponderado = df_hogares.groupby("AGLOMERADO")["PONDERA"].sum()
    viviendas_con_banio = df_hogares[df_hogares["IV9"] == 1].groupby("AGLOMERADO")["PONDERA"].sum()
    # Ahora dividimos las Series (el índice es "AGLOMERADO" en ambos)
    proporcion = (viviendas_con_banio / total_ponderado * 100).fillna(0)
    proporcion.name = "Porcentaje"  # Nombre explícito
    # Convertimos a DataFrame y reset index para mostrar
    proporcion_banio = proporcion.reset_index()
    proporcion_banio["Aglomerado"] = proporcion_banio["AGLOMERADO"].astype(str).replace(AGLOMERADO_ID_A_NOMBRE)
    # Devolvemos solo las columnas que queremos mostrar
    return proporcion_banio[["Aglomerado", "Porcentaje"]]


def grafico_barras_banio(df_banio):
    """
    Genera un gráfico de barras horizontal con los porcentajes de viviendas con baño por aglomerado.
    Args:
        df_banio (pd.DataFrame): DataFrame con columnas "Aglomerado" y "Porcentaje"
    Returns:
        matplotlib.figure: figura lista para usar con st.pyplot()
    """
    # Ordenamos por porcentaje ascendente
    df_ordenado = df_banio.sort_values("Porcentaje", ascending=True)
    # Extraemos 2 series separadas, uno por los nombres de los aglomerados y otro por los porcentajes
    aglomerados = df_ordenado["Aglomerado"]
    porcentajes = df_ordenado["Porcentaje"]

    # Crea una figura y un eje ax para poder dibujar el grafico
    fig, ax = plt.subplots(figsize=(10, 6))
    # BarH es Barra Horizontal, es un gráfico de barras horizontal en dónde
    # En el Eje Y van los aglomerados, en el Eje X los porcentajes.
    ax.barh(aglomerados, porcentajes, color="purple")

    # Título y las labels de los Ejes X y Ejes Y.
    ax.set_title("Porcentaje de viviendas con baño por aglomerado")
    ax.set_xlabel("Porcentaje de viviendas con baño (%)")
    ax.set_ylabel("Aglomerado")
    # Fijamos el rango entre 85 y 100 porque los porcentajes empiezan desde 90% y son muy grandes
    ax.set_xlim(85, 101) 

    # Recorre los valoresde porcentaje y sus índices.
    # Por cada barra, escribe el porcentaje al lado derecho y lo pasa a 0.2 para que sea round
    for i, v in enumerate(porcentajes):
        ax.text(v + 0.2, i, f"{v:.1f}%", va="center", fontsize=9)

    # Para que los valores se puedan leer mejor
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    return fig


#Inciso 1.4.5
def obtener_evolucion_tenencia(df_hogares, option_aglomerados, tenencias_seleccionadas):
    """
    Genera un gráfico de línea que muestra la evolución por trimestre del régimen de tenencia de viviendas 
    para un aglomerado seleccionado, filtrado por los tipos de tenencia elegidos por el usuario.
    Filtra los datos según el aglomerado seleccionado y las tenencias indicadas, agrupa por trimestre y tipo de tenencia, 
    suma la cantidad de hogares, y finalmente genera un gráfico de líneas con Matplotlib que se muestra en Streamlit.
    Args:
        df_hogares (pd.DataFrame): DataFrame con datos de hogares.
        option_aglomerados (str): Nombre del aglomerado seleccionado por el usuario (ej. "Gran Buenos Aires").
        tenencias_seleccionadas (list of str): Lista de nombres de tipos de tenencia.
    """
    # Convertimos las columnas AGLOMERADO y II7 (que tiene régimen de vivienda) a valores numéricos para evitar errores
    df_hogares["AGLOMERADO"] = pd.to_numeric(df_hogares["AGLOMERADO"], errors="coerce")
    df_hogares["II7"] = pd.to_numeric(df_hogares["II7"], errors="coerce")
    df_hogares["TRIMESTRE"] = pd.to_numeric(df_hogares["TRIMESTRE"], errors="coerce")
    # Obtener código del aglomerado desde el nombre
    codigo_aglomerado = None
    for aglomerado_id_str, nombre_aglomerado in AGLOMERADO_ID_A_NOMBRE.items():
        if nombre_aglomerado == option_aglomerados:
            codigo_aglomerado = int(aglomerado_id_str)
            break
    if codigo_aglomerado is None:
        st.warning("No se encontró el código del aglomerado seleccionado.")
        return
    # Filtramos a partir del Aglomerado seleccionado. Hacemos una copia para no modificar el DataFrame original.
    df_filtrado = df_hogares[df_hogares["AGLOMERADO"] == codigo_aglomerado].copy()
    # Si después del filtro el DataFrame queda vacío, entonces significa que no hay datos para ese Aglomerado 
    if df_filtrado.empty:
        st.warning("No hay datos para el aglomerado seleccionado.")
        return
    # Creamos una nueva columna TENENCIA y mapeamos los datos que están dentro de II7 con la constante.
    df_filtrado["TENENCIA"] = df_filtrado["II7"].map(TENENCIA_ID_A_NOMBRE)
    # Ahora filtramos todavía MÁS el DataFrame dejando sólo aquellas filas que correspondan a la tenencia
    # Seleccionada por el usuario. 
    df_filtrado = df_filtrado[df_filtrado["TENENCIA"].isin(tenencias_seleccionadas)]
    # Agrupamos por Trimestre y Tenencia y sumamos la ponderación como valor.
    # Luego el resultado que obtenemos lo convertimos en un DataFrame normal y guardamos esos datos
    # En una nueva columna llamada "Cantidad" -> Dónde va a tener los datos sumados
    ponderado = df_filtrado.groupby(["TRIMESTRE", "TENENCIA"])["PONDERA"].sum().reset_index(name="Cantidad")
    # Pivot toma el dataframe y lo reorganiza para que cada fila represente un trimestre y cada columna un tipo de tenencia. El valor es la cantidad de hogares
    pivot = ponderado.pivot(index="TRIMESTRE", columns="TENENCIA", values="Cantidad").fillna(0)
    # Ordena los trimestres
    pivot = pivot.sort_index()
    # Crea etiquetas para el eje X
    labels_x = []
    for t in pivot.index:
        labels_x.append(f"{int(t)}° Trim.")
    # Crear gráfico
    fig, ax = plt.subplots(figsize=(12, 6))
    # Cada linea representa un tipo de tenencia, el eje X son los trimestres y el eje Y la cantidad de hogares con esa tenencia
    for tenencia in pivot.columns:
        ax.plot(pivot.index, pivot[tenencia], label=tenencia)
    ax.set_xticks(pivot.index)  # usa los valores originales como ubicaciones
    ax.set_xticklabels(labels_x, rotation=45)  # pero con etiquetas personalizadas
    ax.set_title("Evolución del régimen de tenencia por trimestre")
    ax.set_xlabel("Trimestre")
    ax.set_ylabel("Cantidad de hogares")
    ax.legend(title="Tenencia", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    # Mostrar en Streamlit
    st.pyplot(fig)



# Inciso 1.4.6
def obtener_cant_villa_de_emergencia(df_hogares):
    """
    Calcula la cantidad de hogares en villas de emergencia por aglomerado y su porcentaje sobre el total del aglomerado.

    Esta función agrupa los datos por aglomerado, calcula la suma ponderada total de hogares
    y la suma ponderada de aquellos en condición de villa de emergencia (según "IV12_3" == 1).
    Luego construye un DataFrame con ambos valores, calcula el porcentaje relativo,
    ordena los resultados en forma descendente por cantidad de villas y reemplaza los IDs
    de aglomerado por sus nombres.

    Parámetros:
    ----------
    df_hogares : dataframe de hogares

    Devuelve:
    -------
    pandas.DataFrame
        Un DataFrame con columnas: "Aglomerado", "VillasEmergencia" y "Porcentaje",
        ordenado de mayor a menor cantidad de hogares en villas de emergencia.
    """

    # 1) Suma ponderada TOTAL por aglomerado
    total = df_hogares.groupby("AGLOMERADO")["PONDERA"].sum()

    # 2) Suma ponderada de viviendas en villa de emergencia (IV12_3 == 1)
    villas = (
        df_hogares[df_hogares["IV12_3"] == 1]
        .groupby("AGLOMERADO")["PONDERA"]
        .sum()
    )

    # 3) Montamos un DataFrame con ambos, rellenamos 0 donde falte
    df = pd.DataFrame({
        "Total": total,
        "VillasEmergencia": villas
    }).fillna(0)
    
    #sacamos porcentaje
    df["Porcentaje"] = ((df["VillasEmergencia"] / df["Total"]) * 100).round(2).astype(str) + "%"

    # 5) Orden descendente por cantidad de villas
    df = df.sort_values("VillasEmergencia", ascending=False).reset_index()

    # 6) Mapeo de ID nombre 
    df["Aglomerado"] = (
        df["AGLOMERADO"]
        .astype(str)
        .replace(AGLOMERADO_ID_A_NOMBRE)
    )
    return df[["Aglomerado", "VillasEmergencia", "Porcentaje"]]


# Inciso 1.4.7
def obtener_porcentaje_condicion_habitabilidad(df_hogares):
    """
    Calcula el porcentaje de hogares según la condición de habitabilidad dentro de cada aglomerado.

    Agrupa los datos por aglomerado y condición de habitabilidad, suma los valores ponderados 
    ("PONDERA") y calcula el porcentaje relativo dentro de cada aglomerado. 

    Parámetros:
    ----------
    df_hogares: dataframe de hogares

    Devuelve:
    -------
    pandas.DataFrame
        Un DataFrame con columnas: "Aglomerado", "CONDICION_DE_HABITABILIDAD" y "Porcentaje",
        donde cada fila representa el porcentaje de hogares en una condición específica 
        dentro de un aglomerado.
    """

    # Total ponderado por aglomerado 
    total_por_agl = df_hogares.groupby("AGLOMERADO")["PONDERA"].sum()

    # Pondera por aglomerado y condición de habitabilidad 
    cond_por_agl = (
        df_hogares
        .groupby(["AGLOMERADO", "CONDICION_DE_HABITABILIDAD"])["PONDERA"]
        .sum()
        .reset_index()
    )

    # reemplazamos los aglomerados por su id
    cond_por_agl["Aglomerado"] = (
        cond_por_agl["AGLOMERADO"]
        .astype(str)
        .replace(AGLOMERADO_ID_A_NOMBRE)
    )

    # mapeamos el total y rellamos espacios vacios 
    cond_por_agl["Total"] = (
        cond_por_agl["AGLOMERADO"]
        .map(total_por_agl)    # alinea por valor de AGLOMERADO
        .fillna(0)            
    )

    # calculamos el porcentaje
    cond_por_agl["Porcentaje"] = (
        (cond_por_agl["PONDERA"] / cond_por_agl["Total"] * 100)
        .round(2)
        .astype(str)
        + "%"
    )

    return cond_por_agl[["Aglomerado","CONDICION_DE_HABITABILIDAD","Porcentaje"]]


