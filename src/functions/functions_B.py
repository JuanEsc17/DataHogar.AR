from collections import Counter
import csv
from functools import reduce
from pathlib import Path
from functions.functions_comunes import obtener_ultimo_trimestre, obtener_ultimo_trimestre_y_anio
from utils.constantes import AGLOMERADO_ID_A_NOMBRE, DATA_OUT_PATH, REGION_ID_A_NOMBRE,NIVEL_EDUCATIVO_ID_A_NOMBRE
from utils.constantes import DATA_PATH
import pandas as pd

# Le pasamos desde main el archivo hogares y personas   
def process_csv (folder_path):
    """
    Procesa los datasets(lista de diccionario) de hogares e individuos según lo solicitado en cada consigna.
    Args:
    Recibe hogares y personas, ambos list[dict]
    Excepciones:
    En caso de que ocurra cualquier error durante el procesamiento de los archivos (ej: claves faltantes),
    se mostrará un mensaje con los detalles del error.
    """
    file_path_personas = folder_path/ "usu_individuales.csv"
    file_path_hogares = folder_path/ "usu_hogares.csv"
    try:
        # # # Ejercicio 1
        porcentaje_alfabetizacion(file_path_personas)
        # Ejercicio 2
        porcentaje_universitario_extranjero(file_path_personas,input("año: "),input("trimestre: "))
        # Ejercicio 3
        # porcentaje_desocupacion(file_path_personas)
        # Ejercicio 4
        ranking_aglomerados(file_path_hogares, file_path_personas)
        # Ejercicio 5
        porcentaje_propietarios_por_aglomerado(file_path_hogares)
        # Ejercicio 6
        aglomerado_mas_viviendas_dos_ocup_sin_banio(file_path_hogares)
        # Ejercicio 7
        informar_nivel_educativo(file_path_personas)
        # Ejercicio 8
        informar_regiones_descendente(file_path_hogares, file_path_personas)
        # Ejercicio 9
        tabla_aglomerado_nivel_estudio = obtener_mayores_por_nivel_estudio(file_path_personas)
        # Ejercicio 10
        tabla_mayores_secundario_incompleto = calcular_porcentaje_secundario_incompleto(file_path_personas)
        # Ejercicio 11
        aglomerados_mayor_y_menor_viviendasprecarias(file_path_hogares,int(input("año: ")))
        # Ejercicio 12
        porcentaje_jubilados_cond_insuficientes = porcentaje_jubilados_insuficientes(file_path_hogares,file_path_personas)
        # # Ejercicio 13
        cant_personas_universitarios_insuficientes(file_path_hogares,file_path_personas)
    except Exception as e:
        print("Ocurrió un error al procesar los archivos.")
        print(f"Detalles del error: {e}")

# Ejercicio 1
def porcentaje_alfabetizacion(file_path):
    """
        Informa el porcentaje de alfabetización de cada año y del último trimestre, según las personas mayores
        a 6 años.
    """

    analfabetas = dict()
    alfabetas = dict() 
    cantidad = 0
    ultimo_trimestre = None
    ano_actual = None

    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            ano = row["ANO4"]
            
            # Si el año cambió, recalculamos el último trimestre
            if ano != ano_actual:
                ultimo_trimestre = obtener_ultimo_trimestre(ano,file_path)
                ano_actual = ano

            if int(row["TRIMESTRE"]) == ultimo_trimestre and int(row["CH06"]) > 6 :
                cantidad += int(row["PONDERA"])

                if row["CH09"] == "1":
                    alfabetas.setdefault(ano, 0)
                    alfabetas[ano] += int(row["PONDERA"])
                else:
                    analfabetas.setdefault(ano, 0)
                    analfabetas[ano] += int(row["PONDERA"])

    alfabetas_order = dict(sorted(alfabetas.items(), reverse=True))
    analfabetas_order = dict(sorted(analfabetas.items(), reverse=True))

    print(f'-----------------Sección B - Ejercicio 01-------------------------')
    for i in alfabetas_order.items():
        print(f"Porcentaje de alfabetas en el año {i[0]}: % {round((i[1]/cantidad) * 100,2)}")
    for i in analfabetas_order.items():
        print(f"Porcentaje de analfabetas en el año {i[0]}: % {round((i[1]/cantidad) * 100,2)}")

# Ejercicio 2           
def porcentaje_universitario_extranjero(file_path_personas,año,trimestre):
    """
        Informa el porcentaje de aquellas personas extranjeras que hayan cursado el nivel universitario
        o superior

        Args: ingresan como parametros el dataset de individuos ,
        el año y el trimestre a buscar en el archivo para calcular el porcentaje
    """
    df = pd.read_csv(file_path_personas,sep=";",usecols=["ANO4","TRIMESTRE"])
    anios = df["ANO4"].unique().astype(str)
    trimestres = df.groupby("ANO4")["TRIMESTRE"].apply(set).astype(str)
    if año not in anios and trimestre not in trimestres:
        print(f'-----------------Sección B - Ejercicio 02-------------------------')
        print("datos invalidos")
        return
    
    # variables para guardar cantidad
    cant_tot = 0
    cant_extranjeros = 0
    with open(file_path_personas, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        # recorremos el dataset
        for row in reader:
            # si se encuentra en el año y trimestre pasado como parametro
            if row["ANO4"] == año and row["TRIMESTRE"] == trimestre:
                # si se encuentra en nivel universitario o superior agregamos con pondera
                if row["CH12"] in ("7","8"): 
                    cant_tot += int(row["PONDERA"])
                    # si es extranjero (pais limitrofe u otro)
                    if row["CH15"] in ("4","5"):
                        cant_extranjeros += int(row["PONDERA"])
        # si la cantidad es 0 signifca que no hay datos, o no hay archivos para el año y trimestre ingresado o ingreso un año o trimestre no valido
        if (cant_tot == 0):
            print("no se encontraron datos para ese año y trimestre")
            return
        # reonde e imprime porcentaje
        porcentaje = round((cant_extranjeros/cant_tot) * 100, 2)
    print(f'-----------------Sección B - Ejercicio 02-------------------------')
    print(f"porcentaje de extranjeros que cursaron el nivel universitario o superior es del %{porcentaje}")

# Ejercicio 3
def porcentaje_desocupacion(file_path_personas):
    """
        Informa el porcentaje de menor desocupacion. recorriendo el dataset de indiviuos y utilizando 
        un diccionario con diccionarios para guardar y despues recorrer los valores ordenados.

        Args: se pasa como parametro el dataset a recorrer
    """
    # Inicializamos diccionario para ordenar cantidad de desocupacion(por año y trimestre)
    order_estado = dict()
    with open(file_path_personas, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            # si el año no esta en el diccionario lo agregamos
            if row["ANO4"] not in order_estado:
                order_estado[row["ANO4"]] = dict()
            # si el trimestre no esta en el diccionario segun el año lo agregamos e inicializamos
            if row["TRIMESTRE"] not in order_estado[row["ANO4"]]:
                order_estado[row["ANO4"]][row["TRIMESTRE"]] = 0
            # si es desocupado lo agregamos con pondera al diccionario
            if row["ESTADO"] == "2":
                order_estado[row["ANO4"]][row["TRIMESTRE"]] = int(row["PONDERA"])
    # devuelve el año, trimestre y cantidad minima segun la cantidad recorriendo los años y los trimestres por año
    año, trimestre, cant = min(((año,trimestre,cant) for año,trimestres in order_estado.items() for trimestre, cant in trimestres.items()),key=lambda x: x[2])
    print(f'-----------------Sección B - Ejercicio 03-------------------------')
    print(f"en el año {año} trimestre {trimestre} tuvo la menor cantidad de desocupados, siendo {cant}")

## Ejercicio 04 
def ranking_aglomerados(file_path_hogares, file_path_personas):
    """Calcula el ranking de los aglomerados con mayor porcentaje de hogares que tienen al menos dos personas 
    con universidad completa, utilizando los datos del último trimestre y año disponibles.

    Parámetros:
        file_path_hogares (Path): Ruta al archivo CSV de hogares.
        file_path_personas (Path): Ruta al archivo CSV de personas.

    Retorna:
        pd.DataFrame: DataFrame con las siguientes columnas:
            - AGLOMERADO: Identificador del aglomerado.
            - Nombre: Nombre del aglomerado.
            - Porcentaje: Porcentaje de hogares con al menos dos personas con universidad completa.
"""
    #comentado para que no se imprima en streamlit
    #print(f'-----------------Sección B - Ejercicio 04-------------------------')

    # Obtenemos último trimestre y año
    trimestre, anio = obtener_ultimo_trimestre_y_anio(file_path_hogares, file_path_personas)
    #comentado para que no se imprima en streamlit
    #print(f"Usando datos del trimestre {trimestre} del año {anio}")

    df_hogares = pd.read_csv(file_path_hogares, delimiter=';', encoding='utf-8', low_memory=False)
    df_personas = pd.read_csv(file_path_personas, delimiter=';', encoding='utf-8', low_memory=False)

    # 1. Filtramos hogares por año y trimestre
    df_hogares_filtrados = df_hogares[(df_hogares['ANO4'] == anio) & (df_hogares['TRIMESTRE'] == trimestre)].copy()

    # 2. Filtramos a las personas por año, trimestre y por aquellas que tengan nivel educativo = a universitario.
    df_personas_filtradas = df_personas[
        (df_personas['ANO4'] == anio) & 
        (df_personas['TRIMESTRE'] == trimestre) &
        (df_personas['NIVEL_ED'] == 6)
    ].copy()

    # 3. Contamos la cantidad de universitarios cada HOGAR.
    cantidad_universitarios = df_personas_filtradas.groupby(['CODUSU', 'NRO_HOGAR'])['PONDERA'].sum().reset_index(name='CANT_UNIV')

    # 4. Creamos una nueva columna llamada CLAVE que va a tener una tupla con CODUSU Y NRO_HOGAR para poder luego unir personas con hogares
    df_hogares_filtrados['CLAVE'] = list(zip(df_hogares_filtrados['CODUSU'], df_hogares_filtrados['NRO_HOGAR']))
    cantidad_universitarios['CLAVE'] = list(zip(cantidad_universitarios['CODUSU'], cantidad_universitarios['NRO_HOGAR']))

    # 5. Mergeamos ambos DataFrames por CLAVE (CODUSU Y NRO_HOGAR). Así cada hogar tiene la cantidad de universitarios
    df_hogares_cant_universitarios = pd.merge(df_hogares_filtrados, cantidad_universitarios[['CLAVE', 'CANT_UNIV']], on='CLAVE', how='left')
    # 6. Esto es sólo para que en el caso de que haya algún valor erroneo (NAN) lo pasa a 0.
    df_hogares_cant_universitarios['CANT_UNIV'] = df_hogares_cant_universitarios['CANT_UNIV'].fillna(0) 

    # 7. Filtramos los hogares y nos quedamos sólo con aquellos que tengan más de 2 univ.
    df_hogares_con_2mas_uni = df_hogares_cant_universitarios[df_hogares_cant_universitarios['CANT_UNIV'] >= 2].copy()

    # 8. Sumar ponderación de hogares con 2+ universitarios por aglomerado
    hogares_univ_por_aglo = df_hogares_con_2mas_uni.groupby('AGLOMERADO')['PONDERA'].sum()

    # 9. Sumar ponderación total de hogares por aglomerado
    hogares_totales_por_aglo = df_hogares_filtrados.groupby('AGLOMERADO')['PONDERA'].sum()

    # 10. Calcular porcentaje
    porcentajes = (hogares_univ_por_aglo / hogares_totales_por_aglo * 100).round(2).fillna(0)

    top_5 = porcentajes.sort_values(ascending=False).head(5)

    #print("Top 5 aglomerados con mayor porcentaje de hogares con al menos dos personas con universidad completa:")

    # MALE -> Creo un dataframe para devolverlo y así te es más fácil después usar la información, si no te sirve borralo
    # La estructura es AGLOMERADO "2", PORCENTAJE: 12.5%, NOMBRE: LA PLATA. Cambialo si no te sirve!
    df_top_5 = top_5.reset_index()
    df_top_5.columns = ['AGLOMERADO', 'Porcentaje']
    df_top_5['AGLOMERADO'] = df_top_5['AGLOMERADO'].astype(str)
    df_top_5['Nombre'] = df_top_5['AGLOMERADO'].map(AGLOMERADO_ID_A_NOMBRE)

    # Imprimir cada fila con nombre legible y porcentaje
    #informar comentado porque no se usa en streamlit
    #for _, row in df_top_5.iterrows():
    #    print(f"{row['Nombre']}: {row['Porcentaje']}%")

    # Opcional: retornar el DataFrame para seguir usándolo
    return df_top_5[['AGLOMERADO', 'Nombre', 'Porcentaje']]


## Ejercicio 05
def porcentaje_propietarios_por_aglomerado(file_path):
    """
    Calcula e imprime el porcentaje de viviendas ocupadas por propietarios en cada aglomerado.
    Si se cumple la condición de ser propietario, se agrupan los datos por aglomerado y se calcula el porcentaje correspondiente sobre el total 
    de viviendas de ese aglomerado.
    Args: Recibe una lista de diccionarios que representa el dataset de hogares.
    """
    # Este diccionario va a guardar cuentas viviendas hay por aglomerado
    total_viviendas = {}
    # Este diccionario va a guardar cuantas de esas viviendas son de propietarios (según 1 y 2 de II7) por aglomerado
    viviendas_propietarios = {}
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        # Recorremos cada fila del archivo para buscar cuantas viviendas hay y cuantas de ellas son de propietarios según aglomerado.
        for row in reader:
            # Obtenemos el valor de la columna AGLOMERADO para la fila actual.
            aglomerado = row['AGLOMERADO']
            PONDERA = int(row['PONDERA'])
            # Si es la primera vez que leemos ese aglomerado, debemos inicializar el contador en 0.
            if aglomerado not in total_viviendas:
                total_viviendas[aglomerado] = 0
                viviendas_propietarios[aglomerado] = 0
            # Para ese aglomerado, le sumamos +1 se va a ver como clave valor, ej: {'La Plata': 10}
            total_viviendas[aglomerado] += PONDERA
            # Si el valor de la columna II7 es 1 o 2, entonces es propietario y sumamos +1.
            if row['II7'] in ['1', '2']:
                viviendas_propietarios[aglomerado] += PONDERA
        # Informamos para cada aglomerado el porcentaje de viviendas ocupadas por sus propietarios
        print(f"--------------------Sección B - Ejercicio 05----------------------------------")
        print(f"{'Aglomerado':<12} {'% Propietarios':>16}")
        print('-' * 30)
        # Recorremos cada clave del diccionario total_viviendas. La misma tiene los nombres de los aglomerados como key.
        # Cada vez que se ejecuta el bucle del flor, toma una de estas claves y se la asigna a la variable aglomerado.
        # Por cada bucle trabajamos con un aglomerado diferente.
        for aglomerado in total_viviendas:
            ## Cantidad de viviendas totales en ese aglomerado
            total = total_viviendas[aglomerado]
            # Cantidad de propietarios totales por aglomerado
            propietarios = viviendas_propietarios[aglomerado]
            if total > 0:
                porcentaje = (propietarios / total) * 100 
            else: 
                porcentaje = 0
            print(f"{AGLOMERADO_ID_A_NOMBRE[aglomerado]}: {porcentaje:.2f}%")

# Ejercicio 06
def aglomerado_mas_viviendas_dos_ocup_sin_banio(file_path_personas):
    """
    Identifica e imprime el aglomerado con la mayor cantidad de viviendas que no tienen baño 
    y que tengan con más de dos ocupantes.
    La función recorre el listado de hogares y, para cada vivienda que cumpla las condiciones de 
    no tener baño y más de dos ocupantes, cuenta la cantidad ponderada de viviendas en cada aglomerado.
    Args: Recibe el dataset (lista de diccionarios) de hogares 
    """
    # Diccionario para contar viviendas por aglomerado no tienen baño y tienen más de 2 ocupantes
    viviendas_sin_bano_y_mas_de_dos_ocupantes = {}
    with open(file_path_personas, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        # Recorremos cada fila del archivo. Por cada fila vamos a obtener el aglomerado, la cant de ocupantes y si tienen baño o no
        for row in reader:
        # Obtenemos el valor de la columna AGLOMERADO para la fila actual.
            aglomerado = row['AGLOMERADO']
            PONDERA = int(row['PONDERA'])
            #Obtenemos la cantidad de ocupantes por hogar
            ocupantes = int(row['IX_TOT'])
            # Obtenemos si tienen baño o no
            banio = row['II9']
            # Si la vivienda tiene más de 2 ocupantes y no tiene baño (II9 == 04)
            if ocupantes > 2 and banio == '4':
                # Si es la primera vez que encontramos el aglomerado, inicializamos el contador
                if aglomerado not in viviendas_sin_bano_y_mas_de_dos_ocupantes:
                    viviendas_sin_bano_y_mas_de_dos_ocupantes[aglomerado] = 0
                # Si no es la primera vez y cumple con la condición, sumamos +1 a ese aglomerado
                viviendas_sin_bano_y_mas_de_dos_ocupantes[aglomerado] += PONDERA
        
        # Buscamos el aglomerado con más viviendas sin baño y más de 2 ocupantes
        # El max va a tomar todos los key/values (Ej: {'La Plata': 10, 'Berisso': 15,...}) del diccionario y quedarse con el key (es decir
        # el Aglomerado) mayor según el value. (El value lo obtenemos con .get)
        aglomerado_max = max(viviendas_sin_bano_y_mas_de_dos_ocupantes, key=viviendas_sin_bano_y_mas_de_dos_ocupantes.get)
        # Como antes obtuvimos la key(el aglomerado), obtenemos el valor dentro de ese aglomerado.
        cantidad_max = viviendas_sin_bano_y_mas_de_dos_ocupantes[aglomerado_max]    
        # Informar el aglomerado con mayor cantidad de viviendas con más de dos ocupantes y sin baño. Informar también la cantidad de ellas
        print(f"---------------------------Sección B - Ejercicio 06---------------------------------------")
        print(f"Aglomerado con mayor cantidad de viviendas sin baño y más de 2 ocupantes: {AGLOMERADO_ID_A_NOMBRE[aglomerado_max]}")
        print(f"Cantidad de viviendas: {cantidad_max}")    

#Ejercicio 7 
def informar_porcentaje_de_nivel_educativo(diccionario_aglomerados, total_personas_por_aglomerado):
    """
    Informa el porcentaje de personas que han cursado un nivel educativo universitario
    o superior por aglomerado.
    Args:
        diccionario_aglomerados (dict): Diccionario donde la clave es el ID del aglomerado
        y el valor es la cantidad de personas que han cursado un nivel educativo 
        universitario o superior.
    """
    print(f'-----------------Sección B - Ejercicio 07-------------------------')
    print(f"AGLOMERADO \t PORCENTAJE")
    for aglomerado, cantidad in diccionario_aglomerados.items():
        total_personas = total_personas_por_aglomerado.get(aglomerado, 0)
        if total_personas > 0:
            porcentaje = (cantidad/total_personas) * 100
            print(f"{AGLOMERADO_ID_A_NOMBRE[aglomerado]}  %{porcentaje:.2f}")
        else:
            print(f"{AGLOMERADO_ID_A_NOMBRE[aglomerado]}  %0.00")

def informar_nivel_educativo(file_path_personas):
    """
    Analiza el archivo 'usu_individuales.csv' y guarda en un diccionario las personas
    que cursan o han cursado un nivel educativo universitario o superior, agrupando
    por aglomerado. Luego, imprime el porcentaje de personas por cada aglomerado. 
    
    Returns:
        No retorna ningun resultado, pero imprime el porcentaje de personas que han 
        cursado un nivel educativo universitario o superior por aglomerado.
    """
    #diccionario para guardar los aglomerados y la cantidad de personas de cada uno que curso universitario o superior
    diccionario_aglomerados = {}
    total_personas_por_aglomerado = {}
    #abro el archivo
    with open(file_path_personas, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            # Guardo los valores que voy a utilizar
            numero_aglomerado = row['AGLOMERADO']
            nivel_educativo = int(row['CH12'])
            pondera = int(row['PONDERA'])

            # Inicializar el total de personas por aglomerado si no existe
            if numero_aglomerado not in total_personas_por_aglomerado:
                total_personas_por_aglomerado[numero_aglomerado] = 0
            total_personas_por_aglomerado[numero_aglomerado] += pondera

            # Si cumple con el nivel educativo universitario o superior
            if nivel_educativo == 7 or nivel_educativo == 8:
                if numero_aglomerado not in diccionario_aglomerados:
                    diccionario_aglomerados[numero_aglomerado] = 0
                diccionario_aglomerados[numero_aglomerado] += pondera
    #ordeno los aglomerados por numero de aglomerado (para que se vea de la forma como esta en el EPH)
    diccionario_aglomerados = dict(sorted(diccionario_aglomerados.items(), key=lambda item: int(item[0]), reverse=False))
    
    total_personas_por_aglomerado = dict(sorted(total_personas_por_aglomerado.items(), key=lambda item: int(item[0]), reverse=False))
    #informo los resultados
    informar_porcentaje_de_nivel_educativo(diccionario_aglomerados, total_personas_por_aglomerado)


#Ejercicio 8

def informar_porcentaje_de_inquilinos_por_region(porcentaje_inquilinos):
    """
    Informa el porcentaje de inquilinos por región.
    Args:
        porcentaje_inquilinos (Series): Series que tiene la región como índice
        y el porcentaje de inquilinos como valor.
        total_personas_por_region (dict): Diccionario donde la clave es el ID de la región
        y el valor es el total de personas en esa región.
    """
    print(f'-----------------Sección B - Ejercicio 08-------------------------')
    print(f"REGION \t PORCENTAJE")
    for region, porcentaje in porcentaje_inquilinos.items():
        nombre_region = REGION_ID_A_NOMBRE.get(str(region), f"Región {region}")
        print(f"{nombre_region}  %{porcentaje:.2f}")


def informar_regiones_descendente(file_path_hogares, file_path_personas):
    """
    Calcula e informa el porcentaje de inquilinos por región a partir de hogares e individuos.
    Args:
        file_path_hogares (Path): Ruta al archivo CSV de hogares.
        file_path_personas (Path): Ruta al archivo CSV de individuos.
    Returns:
        No retorna ningún resultado, pero imprime el porcentaje de inquilinos por región en orden descendente según el porcentaje.
    """
    #cargo los datos en df de hogares e invidiuos
    hogares_df = pd.read_csv(file_path_hogares, delimiter=';', encoding='utf-8', low_memory=False)
    personas_df = pd.read_csv(file_path_personas, delimiter=';', encoding='utf-8', low_memory=False)

    # Convertir PONDERA y II7 a tipo numérico y eliminar valores nulos
    hogares_df['PONDERA'] = pd.to_numeric(hogares_df['PONDERA'], errors='coerce')
    hogares_df['II7'] = pd.to_numeric(hogares_df['II7'], errors='coerce')
    personas_df['PONDERA'] = pd.to_numeric(personas_df['PONDERA'], errors='coerce')

    #borro los valores nulos de las columnas que voy a utilizar
    hogares_df = hogares_df.dropna(subset=['PONDERA', 'REGION', 'II7'])
    personas_df = personas_df.dropna(subset=['PONDERA', 'REGION'])

    #filtro por la columna (II7) que indica si es inquilino o no
    hogares_inquilinos = hogares_df[hogares_df['II7'] == 3.0]

    #agrupo los datos de region por cuantos hogares hay en la region
    inquilinos_por_region = hogares_inquilinos.groupby('REGION')['PONDERA'].sum()

    #agrupo las regiones por la cantidad total de personas
    total_personas_por_region = personas_df.groupby('REGION')['PONDERA'].sum()

    # Asegurarte de que las regiones coincidan
    regiones_comunes = inquilinos_por_region.index.intersection(total_personas_por_region.index)
    inquilinos_por_region = inquilinos_por_region.loc[regiones_comunes]
    total_personas_por_region = total_personas_por_region.loc[regiones_comunes]

    #calculo el porcentaje por region
    porcentaje_inquilinos = (inquilinos_por_region / total_personas_por_region) * 100
    #ordeno el resultado de mayor a menor
    porcentaje_inquilinos = porcentaje_inquilinos.sort_values(ascending=False)

    # Informar los resultados
    informar_porcentaje_de_inquilinos_por_region(porcentaje_inquilinos)

#Ejercicio 9:

def creo_tabla_nivel_educativo(tabla_agrupada, aglomerado):
    """
    Crea una tabla con los datos agrupados por año, trimestre y nivel educativo.
    Args:
        tabla_agrupada (pd.Series): Serie agrupada con los datos de año, trimestre, nivel educativo y ponderación.
        aglomerado (int): ID del aglomerado seleccionado.
    Returns:
        list: Lista de listas que representa la tabla de los niveles educativos del aglomerado.
    """
    # Crear el encabezado de la tabla
    encabezado = ["Año", "Trimestre"] + list(NIVEL_EDUCATIVO_ID_A_NOMBRE.values())
    tabla = [encabezado]

    # Iterar sobre los datos agrupados para construir las filas
    datos_por_anio_trimestre = {}
    for (anio, trimestre, nivel_educativo), pondera in tabla_agrupada.items():
        if (anio, trimestre) not in datos_por_anio_trimestre:
            datos_por_anio_trimestre[(anio, trimestre)] = {nivel: 0 for nivel in NIVEL_EDUCATIVO_ID_A_NOMBRE.keys()}
        datos_por_anio_trimestre[(anio, trimestre)][str(nivel_educativo)] = pondera  # Convertir nivel educativo a string para coincidir con las claves

    for (anio, trimestre), niveles in datos_por_anio_trimestre.items():
        fila = [anio, trimestre]
        for nivel_educativo in NIVEL_EDUCATIVO_ID_A_NOMBRE.keys():
            fila.append(niveles.get(nivel_educativo, 0))
        tabla.append(fila)

    # Imprimir la tabla
    print(f"Aglomerado: {AGLOMERADO_ID_A_NOMBRE[str(aglomerado)]}")
    print(f"{' | '.join(encabezado)}")
    print("-" * (len(encabezado) * 15))
    for fila in tabla[1:]:  # Excluye el encabezado para imprimir solo las filas
        print(f"{' | '.join(map(str, fila))}")

    return tabla
def obtener_aglomerado_valido():
    """
    Pide al usuario que ingrese un número de aglomerado válido y lo devuelve.
    Returns:
        int: Número de aglomerado válido.
    """
    #aglomerados disponibles
    print("Listado de aglomerados disponibles:")
    for id_aglo, nombre in AGLOMERADO_ID_A_NOMBRE.items():
        print(f"{id_aglo}: {nombre}")
    #pido al usuario que ingrese el aglomerado por teclado en un while para que ponga un nombre valido
    while True:
        try:
            aglomerado = int(input("Ingrese el numero de aglomerado: "))
            #si el numero no es de un aglomerado valido, le pido que ingrese otro
            if str(aglomerado) not in AGLOMERADO_ID_A_NOMBRE:
                print("El aglomerado no es válido, intente nuevamente.")
                continue
            #si era el valido lo retorno
            return aglomerado
        #si el usuario no ingresa un numero entero, le pido que ingrese otro
        except ValueError:
            print("El aglomerado no es válido, ingrese un número entero.")

def obtener_mayores_por_nivel_estudio(file_path_personas):
    """
    Calcula e informa en una tabla la cantidad de personas mayores a 18 años dependiendo su nivel educativo por trimestre y año.
    Args:
        file_path_personas (Path): Ruta al archivo CSV de personas.
    Returns:
        list: Lista de listas que representa la tabla de los niveles educativos del aglomerado.
    """
    # Verificar que el aglomerado sea válido
    aglomerado = obtener_aglomerado_valido()

    # Cargar los datos de personas con Pandas
    personas_df = pd.read_csv(file_path_personas, delimiter=';', encoding='utf-8', low_memory=False)
    
    # Convertir columnas necesarias a tipo numérico
    personas_df['CH06'] = pd.to_numeric(personas_df['CH06'], errors='coerce')
    personas_df['AGLOMERADO'] = pd.to_numeric(personas_df['AGLOMERADO'], errors='coerce')
    personas_df['ANO4'] = pd.to_numeric(personas_df['ANO4'], errors='coerce')
    personas_df['TRIMESTRE'] = pd.to_numeric(personas_df['TRIMESTRE'], errors='coerce')
    personas_df['PONDERA'] = pd.to_numeric(personas_df['PONDERA'], errors='coerce')

    # Filtrar personas mayores de 18 años y del aglomerado seleccionado
    personas_filtradas = personas_df[
        (personas_df['CH06'] >= 18) & (personas_df['AGLOMERADO'] == aglomerado)
    ]
   
    # Agrupar por año, trimestre y nivel educativo, sumando la ponderación
    tabla_agrupada = personas_filtradas.groupby(['ANO4', 'TRIMESTRE', 'NIVEL_ED'])['PONDERA'].sum()

    # Crear la tabla usando la función separada
    tabla = creo_tabla_nivel_educativo(tabla_agrupada, aglomerado)

    return tabla

#Ejercicio 10:


def calcular_porcentaje_secundario_incompleto(file_path_personas):
    """
    Calcula el porcentaje de personas con "Secundario incompleto" en dos aglomerados seleccionados
    para cada combinación de año y trimestre, basándose en un archivo CSV de datos individuales.

    La función pide al usuario que ingrese dos números de aglomerados (A y B), luego lee los datos
    del archivo "usu_individuales.csv", procesa la información de cada persona para determinar su 
    nivel educativo, y calcula el porcentaje de personas con "Secundario incompleto" en cada aglomerado
    por año y trimestre.

    Parámetros:
        Ninguno. La función solicita los datos de entrada al usuario a través de `input()`.

    Retorna:
        list: Una lista de diccionarios, donde cada diccionario contiene la información de un año y
            trimestre, con los porcentajes de "Secundario incompleto" para los aglomerados A y B.

    El formato de la tabla resultante es:
        [
            {"Año": <año>, "Trimestre": <trimestre>, "Aglomerado A": <porcentaje_A>, "Aglomerado B": <porcentaje_B>},
            ...
        ]

    Del archivo CSV de entrada se utilizan las siguientes columnas:
        - CH06: Edad de la persona.
        - AGLOMERADO: Número de aglomerado.
        - ANO4: Año del registro.
        - TRIMESTRE: Trimestre del registro.
        - NIVEL_ED_str: Nivel educativo de la persona.
        - PONDERA: Ponderación (peso) de la persona.

    La función ignora a personas menores de 18 años, y solo calcula los porcentajes para los aglomerados
    especificados por el usuario.
    
    Ejemplo de uso:
        tabla = calcular_porcentaje_secundario_incompleto()
        for fila in tabla:
            print(fila)
    """
    print(f'-----------------Sección B - Ejercicio 10-------------------------')
    print("Seleccione 2 números de aglomerados de la siguiente lista: ")
    for id_aglo, nombre in AGLOMERADO_ID_A_NOMBRE.items():
        print(f"{id_aglo}: {nombre}")

    #pido al usuario que ingrese los 2 aglomerados por teclado
    aglo_a = int(input("Ingrese número de aglomerado A: "))
    aglo_b = int(input("Ingrese número de aglomerado B: "))

    #los datos para armar la tabla los voy a guardar en un diccionario:
    data = {}
    with open(file_path_personas, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            try:
                edad = int(row["CH06"])         #c/ dato que necesito lo guardo en una variable
                aglomerado = int(row["AGLOMERADO"])
                anio = int(row["ANO4"])
                trimestre = int(row["TRIMESTRE"])
                nivel_educativo = row["NIVEL_ED_str"]
                pondera = int(row["PONDERA"])
            except ValueError:
                continue  # Saltear filas con errores

                #ahora empiezo con las condiciones que me pide el enunciado:
            if edad < 18:
                continue  # Solo adultos

            if aglomerado not in [aglo_a, aglo_b]:
                continue  # Solo aglomerados seleccionados
                
                #creo una clave que combina anio, trimestre y aglomerado(ej (2020, 1, 32) --> Año 2020, trimestre 1, aglomerado 32)
            clave = (anio, trimestre, aglomerado)
            if clave not in data:       #Si esa clave no existe todavía en mi nuevo dic data, entonces la crea y le pone como valores 0
                data[clave] = {"total": 0, "secundario_incompleto": 0}

                #ahora sumamos 1 al total de personas mayores de 18 años para ese (año, trimestre, aglomerado).
            data[clave]["total"] += pondera
                #si esa persona tiene nivel educativo "secundario incompleto", entonces suma 1 en la cuenta
            if nivel_educativo == "Secundario incompleto":
                data[clave]["secundario_incompleto"] += pondera

    # Ahora armamos la tabla que vamos a imprimir con los datos
    tabla = []

    # Obtener todos los (anio, trimestre) únicos
    #armamos una lista ordenada de todos los (año, trimestre) que aparecen en el data.
    periodos = sorted(set((anio, trimestre) for (anio, trimestre, _) in data.keys()))
    #De cada clave, agarramos sólo el año y el trimestre (ignoramos el aglomerado con el _).
    #generamos pares como por ej 2020, 1

    for anio, trimestre in periodos:
        fila = {"Año": anio, "Trimestre": trimestre, "Aglomerado A": "", "Aglomerado B": ""}

        # Aglomerado A
        clave_a = (anio, trimestre, aglo_a)
        if clave_a in data:
            total = data[clave_a]["total"]
            secundarios = data[clave_a]["secundario_incompleto"]
            porcentaje = (secundarios / total) * 100 if total > 0 else 0
            fila["Aglomerado A"] = f"{round(porcentaje)}%"

        # Aglomerado B
        clave_b = (anio, trimestre, aglo_b)
        if clave_b in data:
            total = data[clave_b]["total"]
            secundarios = data[clave_b]["secundario_incompleto"]
            porcentaje = (secundarios / total) * 100 if total > 0 else 0
            fila["Aglomerado B"] = f"{round(porcentaje)}%"

        tabla.append(fila)
    # imprimo la tabla en un formato legible
    print("\nPorcentaje de personas con secundario incompleto (18 años o más):\n")
    print(f"{'Año':<6} {'Trimestre':<10} {'Aglomerado A':<15} {'Aglomerado B':<15}")
    print("-" * 50)
    for fila in tabla:
      print(f"{fila['Año']:<6} {fila['Trimestre']:<10} {fila['Aglomerado A']:<15} {fila['Aglomerado B']:<15}")
    return tabla
    
#Ejercicio 11 Seccion B- aglomerados con mayor y menor porcentaje de viviendas precarias

def aglomerados_mayor_y_menor_viviendasprecarias(file_path_hogares, anio):
    """
    Calcula y muestra el aglomerado con el mayor y menor porcentaje de viviendas precarias
    en un año y trimestre específicos.

    El usuario ingresa un año, y la función determina el último trimestre disponible. Luego,
    analiza los registros de viviendas del archivo "usu_hogares.csv" para calcular los porcentajes
    de viviendas precarias (según los criterios de material de techo y piso).

    Imprime:
        - El aglomerado con el mayor y menor porcentaje de viviendas precarias.
        - El total de viviendas y viviendas precarias en ambos aglomerados.

    """
    print(f'-----------------Sección B - Ejercicio 11-------------------------')
    
    # Primero encontramos el último trimestre disponible para ese año
    
    ultimo_trimestre = obtener_ultimo_trimestre(anio,file_path_hogares)

    # Ahora procesamos los datos como antes, usando el último trimestre detectado
    # Definimos 2 diccionarios para contar totales y precarios por aglomerado
    total_por_aglomerado = {}
    precarios_por_aglomerado = {}
    # Contador para saber si se encontraron datos válidos--> esto lo tuve que agergar porque si ignreso un año que no esta en los registros tira error
    registros_encontrados = 0
    with open(file_path_hogares, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        # Iteramos sobre cada fila del archivo
        for row in reader:
            # Filtramos solo los registros del año solicitado y el cuarto trimestre que es el ultimo.
            if row["ANO4"] == str(anio) and row["TRIMESTRE"] == str(ultimo_trimestre):
                #print(row["IV3"], row["MATERIAL_TECHUMBRE"]) lo hice para ver por que los porcentajes daban tan bajos a ver si tenia sentido.. 
                registros_encontrados += 1
                # Obtenemos el código del aglomerado
                cod_aglomerado = row["AGLOMERADO"]

                # Inicializamos vacío si no están en nuestro diccionario
                if cod_aglomerado not in total_por_aglomerado:
                    total_por_aglomerado[cod_aglomerado] = 0
                    precarios_por_aglomerado[cod_aglomerado] = 0
                # Incrementamos el contador de viviendas totales para este aglomerado
                total_por_aglomerado[cod_aglomerado] += int(row["PONDERA"])

                # Verificamos si esta vivienda es precaria según los criterios: material techumbre que es un columna generada en la seccion A
                # Y el criterio de material del piso que si es 3 significa: ladrillo suelto/tierra --> osea precario
                if row["IV3"] == "3" and row["MATERIAL_TECHUMBRE"] == "Material precario":
                    precarios_por_aglomerado[cod_aglomerado] += int(row["PONDERA"])

                if registros_encontrados == 0:
                    print(f"No se encontraron registros para el año {anio} en el trimestre {ultimo_trimestre}.")
                    return
                
    # Calculamos porcentaje por aglomerado
    porcentaje_por_aglomerado = {}
    for aglo in total_por_aglomerado:
        #por cada aglomerado en el diccionario nos guardamos la cantidad en una variable local
        total = total_por_aglomerado[aglo]
        precarios = precarios_por_aglomerado[aglo]
        porcentaje = ((precarios / total)) * 100 if total > 0 else 0
        #guardamos ese resultado obtenido en un nuevo diccionarios
        porcentaje_por_aglomerado[aglo] = porcentaje 

    aglomerado_max = max(porcentaje_por_aglomerado, key=porcentaje_por_aglomerado.get)
    aglomerado_min = min(porcentaje_por_aglomerado, key=porcentaje_por_aglomerado.get)

    print(f"Año analizado: {anio}, Trimestre: {ultimo_trimestre}")
    #print(f"Aglomerado con mayor porcentaje de viviendas precarias: {aglomerado_max} ({porcentaje_por_aglomerado[aglomerado_max]:.2f}%)")
    # Probando hacer el print cn el nombre del aglomerado en vez del numero:
    print(f"Aglomerado con mayor porcentaje de viviendas precarias: {AGLOMERADO_ID_A_NOMBRE.get(aglomerado_max, aglomerado_max)} ({porcentaje_por_aglomerado[aglomerado_max]:.2f}%)")
    print(f"Aglomerado con menor porcentaje de viviendas precarias: {AGLOMERADO_ID_A_NOMBRE.get(aglomerado_min, aglomerado_min)} ({porcentaje_por_aglomerado[aglomerado_min]:.2f}%)")
    print(f"{AGLOMERADO_ID_A_NOMBRE.get(aglomerado_max, aglomerado_max)} tiene {total_por_aglomerado[aglomerado_max]} viviendas registradas en el trimestre y de viviendas precarias: {precarios_por_aglomerado[aglomerado_max]}.")
    print(f"{AGLOMERADO_ID_A_NOMBRE.get(aglomerado_min, aglomerado_min)} tiene {total_por_aglomerado[aglomerado_min]} viviendas registradas en el trimestre y precarias: {precarios_por_aglomerado[aglomerado_min]}.")


# Ejercicio 12
def porcentaje_jubilados_insuficientes(file_path_hogares,file_path_personas):
    """
    Calcula el porcentaje de jubilados que viven en viviendas insuficientes por aglomerado en
    el ultimo trimestre de 2024.

    Returns: Diccionario con porcentaje de jubilados en viviendas insuficientes por aglomerado.
    """
    print(f'-----------------Sección B - Ejercicio 12 -------------------------')
    hogares_insuficientes = set()
    ult_tri, ult_anio = obtener_ultimo_trimestre_y_anio(file_path_personas, file_path_hogares)
    print(f"Último trimestre: {ult_tri}, Último año: {ult_anio}")
    # Recorro los hogares y guardo los que cumplen con la condicion de insuficiencia en una tupla
    with open(file_path_hogares, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if int(row["ANO4"]) == ult_anio and int(row["TRIMESTRE"]) == ult_tri:
                if row["CONDICION_DE_HABITABILIDAD"] == "Insuficiente":
                    hogares_insuficientes.add(row["CODUSU"])

    total_jubilados = {}
    jubilados_insuficientes = {}
    with open(file_path_personas, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
    # Recorro los individuos y cuento los que cumplen con la condicion de insuficiencia y que son jubilados
        for row in reader:
            if int(row["ANO4"]) == ult_anio and int(row["TRIMESTRE"]) == ult_tri:
                if row["CAT_INAC"] == "1":
                    total_jubilados[row["AGLOMERADO"]] = total_jubilados.get(row["AGLOMERADO"], 0) + int(row["PONDERA"])
                    if row["CODUSU"] in hogares_insuficientes:
                        jubilados_insuficientes[row["AGLOMERADO"]] = jubilados_insuficientes.get(row["AGLOMERADO"], 0) + int(row["PONDERA"])

    ## Calculo el porcentaje de jubilados en viviendas insuficientes por aglomerado
    porcentajes = {}
    for aglomerado in total_jubilados:
        total = total_jubilados[aglomerado]
        insuf = jubilados_insuficientes.get(aglomerado, 0)
        porcentaje = (insuf / total) * 100 if total > 0 else 0
        porcentajes[AGLOMERADO_ID_A_NOMBRE[aglomerado]] = round(porcentaje, 2)
    for aglo_id, nombre in AGLOMERADO_ID_A_NOMBRE.items():
        if aglo_id in total_jubilados:
            total = total_jubilados[aglo_id]
            porcentaje = porcentajes.get(nombre, 0)
            print(f"{nombre}: {porcentaje}%  (Total jubilados: {total})")
    return porcentajes

# Ejercicio 13

def cant_personas_universitarios_insuficientes(file_path_hogares, file_path_personas):
    """
    Calcula la cantidad de personas que han cursado universidad o superior
    en condiciones de vivienda insuficientes para un año y trimestre dados por el usuario.

    Imprime la cantidad de personas que cumplen con la condición.
    """
    anio = input("Ingrese el año: ")
    # Arreglar lo del trimestre, sino no va a andar
    trimestre_hogares = obtener_ultimo_trimestre(anio,file_path_hogares)
    trimestre_individuos = obtener_ultimo_trimestre(anio,file_path_personas)

    if (trimestre_hogares == trimestre_individuos):
        trimestre = trimestre_individuos
        # Creo una lista con los numeros de hogar que cumplen con la condicion de insuficiencia
        hogares_validos = set()
        with open(file_path_hogares, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row["ANO4"] == anio and row["TRIMESTRE"] == trimestre:
                    if row["CONDICION_DE_HABITABILIDAD"] == "Insuficiente":
                        hogares_validos.add(row["CODUSU"])
        cant = 0
        # Recorro los individuos y cuento los que cumplen con la condicion de insuficiencia y que hayan cursado universidad o superior
        with open(file_path_personas, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row["ANO4"] == anio and row["TRIMESTRE"] == trimestre:
                    if row["CODUSU"] in hogares_validos and row["CH12"] in ["7", "8"]: 
                        cant += int(row["PONDERA"])
        print(f"Cantidad de personas que hayan cursado universidad o superior en condiciones insuficientes: {cant}")
    else:
        print("Los trimestres de los archivos no coinciden")
