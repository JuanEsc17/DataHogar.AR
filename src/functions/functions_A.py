from collections import Counter
import csv
from functools import reduce
from pathlib import Path
from utils.constantes import AGLOMERADO_ID_A_NOMBRE, DATA_OUT_PATH
from utils.constantes import DATA_PATH

## Sección A: Ejercicio 02
# Combinamos varios archivos (hogares/individuales).
# Recibimos el nombre del archivo, dónde se encuentran en la carpeta, cuál es su archivo de salida y su función correspondiente
# (son distintos según si son hogares o individuos)
def transform_files (file_names, folder_path, output_filename, apply_changes_func):
    """
    Combina y transforma varios archivos de entrada en un único archivo CSV de salida.
    Esta función se encarga de:
    - Buscar y leer todos los archivos que coincidan con el patrón `usu_individual_*/usu_hogar_*` dentro de `folder_path(files)`.
    - Aplica una función de transformación (`apply_changes_func`) a cada fila de los archivos.
    - Escribe todas las filas transformadas en un nuevo archivo CSV (`output_filename(usu_hogares/usu_individuales)`), incluyendo una única vez el encabezado.
    Arms: file_names (es el patrón de búsqueda), folder_path(la ruta dónde están los archivos de entrada), output_filename(nombre de salida del archivo),
    apply_changes(es la función que transforma y modifica cada fila del archivo original, que es diferente para hogares o individuos)
    """
    se_escribio_encabezado = False
    output_file = DATA_OUT_PATH / output_filename
    # creamos el archivo nuevo y lo abrimos como escritura
    with output_file.open("w", encoding="utf-8", newline="") as salida:
    # El .glob matchea según un patrón especifico que le pasamos. En este caso le pasamos el nombre con el que empiezan los archivos
        for file in folder_path.glob(file_names):
            # Abrimos los archivos a unir
            with open(file, encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';') 
                # Por cada fila vamos a aplicar los cambios por primera vez que agregan encabezados         
                for row in reader:
                    apply_changes_func(row)
                    # Si el encabezado todavía no se escribió, entonces 
                    if (not se_escribio_encabezado):
                        # Agarramos la fila que modificamos la 1era vez, le pedimos sus keys y la agregamos al encabezado.
                        encabezado_modificado = list(row.keys())
                        # Creamos un DictWriter utilizando las columnas que obtuvimos a partir de haber modificado la 1era fila.
                        writer = csv.DictWriter(salida, fieldnames = encabezado_modificado, delimiter=';')
                        # Escribimos el encabezado a partir de fieldnames.
                        writer.writeheader()
                        se_escribio_encabezado = True
                    writer.writerow(row)
    return 

# Función que vamos a utilizar para recorrer el dataset 1 sola vez.
# Cada individuo es una FILA.
def apply_changes_individuos(individuo):
    # Recibimos individuos y el for no es necesario
        add_column_ch04_str(individuo)    
        add_nivel_ed_str(individuo)
        add_cond_laboral(individuo) #agrego funcion punto 05 seccion A
        add_universitario_num(individuo) #funcion punto 06 seccion A


## Sección A: Ejercicio 03 - Información individuos
def add_column_ch04_str(individuo):
    """
    Agrega una nueva columna al diccionario con el valor en str según el genero ('CH04') del individuo.
    Args: Recibe a un individuo del diccionario con los datos originales del archivo CSV.
    """
    # Leemos el valor original de CH04 
    value = individuo["CH04"]
    if value == '1':
        genero = "Masculino"
    else:
        genero = "Femenino"
    # Agregamos el nuevo value y el valor
    individuo['CH04_str'] = genero


## Sección A: Ejercicio 04 - Información individuos
def add_nivel_ed_str(individuo):
    """
    Agrega una nueva columna al diccionario con el valor en str según su nivel educativo ('NIVEL_ED').
    Args: Recibe a un individuo del diccionario con los datos originales del archivo CSV.
    """
    value = individuo["NIVEL_ED"]
    match value:
        case "1": 
            ed ="Primario incompleto"
        case "2":
            ed ="Primario completo"
        case "3":
            ed ="Secundario incompleto"
        case "4":
            ed ="Secundario completo"
        case "5" | "6":
            ed="Superior o universitario"
        case _:
            ed ="Sin informacion"
    individuo['NIVEL_ED_str'] = ed

#Seccion A: ejercicio 05- CONDICION LABORAL

def add_cond_laboral(individuo):
    """
    Asigna la condición laboral de un individuo en función de su estado y categoría ocupacional.

    La función evalúa el estado laboral y la categoría ocupacional de un individuo para asignarle
    una etiqueta correspondiente, como "Ocupado autónomo", "Ocupado dependiente", "Desocupado",
    "Inactivo" o "Fuera de categoría/sin información". Luego, la condición laboral se guarda en
    la columna 'COND_LAB_str' del diccionario 'individuo'.
    """
    #guardo las columnas que voy a necesitar en variables:
    estado = individuo["ESTADO"]
    cat_ocup = individuo["CAT_OCUP"]

    if (estado == "1"):
        if(cat_ocup == "1" or cat_ocup =="2"):
            cond_lab = "Ocupado autónomo"
        else:
            cond_lab = "Ocupado dependiente"
    elif (estado == "2"):
        cond_lab = "Desocupado"
    elif (estado == "3"):
        cond_lab = "Inactivo"
    elif (estado == "4"):
        cond_lab = "Fuera de categoría/sin información"
    else:
        cond_lab = "" #agregué esta opc de string vacio porque en ESTADO hay una opcion de rta que es 0(el enunciado no la incluye), que son las personas que no respondieron
    individuo['COND_LAB_str']= cond_lab

#Seccion A ejercicio 06 - Universitario numerico
#funcion para saber si una persona COMPLETO el nivel universitario (el enunciado esta redactado raro pero yo interprete que SOLO los que terminaron son valor 1)
def add_universitario_num(individuo):
    """
    Asigna un valor numérico al nivel educativo universitario de un individuo.

    La función evalúa la edad y el nivel educativo de un individuo para asignar el valor correspondiente:
    - 1 si es mayor de 18 años y tiene nivel educativo universitario (nivel "6").
    - 0 si es mayor de 18 años y no tiene nivel universitario.
    - 2 si es menor de 18 años.
    """
    #guardo las columnas que voy a necesitar en variables(edad y nivel educativo):
    edad = int(individuo['CH06'])
    nivel_ed = individuo['NIVEL_ED']
    if edad >= 18:
        if nivel_ed == "6":
            nivel_uni = 1
        else:
            nivel_uni = 0
    else:
        nivel_uni = 2
    individuo['UNIVERSITARIO_num'] = nivel_uni
    


##Ejercicios con hogares
def apply_changes_hogares(hogar):
        add_tipo_hogar(hogar)
        add_MATERIAL_TECHUMBRE(hogar)
        add_densidad_hogar(hogar)
        add_condicion_de_habitabilidad(hogar)

#Seccion A: Ejercicio 07 - Informacion hogares


def add_tipo_hogar(hogar):
    """ 
    Se asigna un tipo de hogar según la cantidad de personas que lo habitan ('IX_TOT') y se agrega al hogar el tipo de hogar 

    Args:
        hogar(diccionario): es un diccionario que contiene la informacion de un hogar, que tiene IX_TOT como clave

    Returns:
        No se retorna nada, se modifica el diccionario, pero añade la clave TIPO_HOGAR al hogar
    """
    #Se utiliza try para evitar errores en caso de que el valor no sea un entero
    try: 
        value = int(hogar['IX_TOT'])
        #1 es unipersonal
        #2, 3, 4 son nucleares
        #5 o mas son extendidos
        if value == 1:
            tipo_hogar = "Unipersonal"
        elif value >= 2 and value <= 4:
            tipo_hogar = "Nuclear"
        elif value >= 5:
            tipo_hogar = "Extendido"
        else:
            tipo_hogar = "Sin informacion"
    except ValueError:
        tipo_hogar = "Sin informacion"
    hogar['TIPO_HOGAR'] = tipo_hogar



#Seccion A: Ejercicio 08 - Material de techumbre


def add_MATERIAL_TECHUMBRE(hogar): 
    """
    Se asigna un tipo de material de techumbre según la categoria ('IV4') y se agrega al hogar el tipo de material de techumbre    
    
    Args:
        hogar(diccionario): es un diccionario que contiene la informacion de un hogar, que tiene IV4 como clave

    Returs:
        No se retorna nada, se modifica el diccionario, pero añade la clave MATERIAL_TECHUMBRE al hogar
    """
    #Se utiliza try para evitar errores en caso de que el valor no sea un entero
    try:
        # Se usa la IV4 porque es la segun el archivo deja ver varios valores
        value = int(hogar['IV4'])
        #de 1 a 4 es material durable
        #de 5 a 7 es material precario
        #9 no aplica
        #el resto sin info
        if 1 <= value <= 4:
            material_techumbre = "Material durable"
        elif 5 <= value <= 7:
            material_techumbre = "Material precario"
        elif value == 9:
            material_techumbre = "No aplica"
        else:
            material_techumbre = "Sin informacion"
    except ValueError:
        material_techumbre = "Sin informacion"
    hogar['MATERIAL_TECHUMBRE'] = material_techumbre

# Seccion A: Ejercicio 09 - Densidad de Hogar
def add_densidad_hogar(hogar):
    """
        Agrega una columna segun el nivel de densidad del hogar que es calculado a partir de la cantidad 
        de personas y habitaciones que tenga el hogar.

        Args: le llega como parametro el dataset de hogares, el cual se modificara en el output
    """
    # intento tranformar en entero y si no hay valor o hay otro tipo tira error (ValueError,TypeError)
    try:
        cant_habitaciones = int(hogar["IV2"])
        cant_personas = int(hogar["IX_TOT"])
        # si la cantidad de personas es menor a la cantidad de habitaciones es densidad baja
        if cant_personas < cant_habitaciones: 
            densidad = "baja"
        # sino si hay entre una o dos personas por habitacion la densidad es media
        elif cant_personas == cant_habitaciones or cant_personas/2 <= cant_habitaciones:
            densidad = "media"
        # sino, es mayor la cantidad de personas que habitaciones por lo tanto es alta
        else:
            densidad = "alta"
    except (ValueError, TypeError):
        densidad = "Sin información"
    hogar["DENSIDAD_HOGAR"] = densidad


#Seccion A: Ejercicio 10 - Condicion de habitabilidad
def calculate_condition(puntaje):
    """
      Defino la condicion de habitabilidad segun el puntaje

      Args: Recibe el puntaje que se calcula a partir de la cantidad de condiciones que cumple el hogar
      
      Returns: Devuelve la condicion de habitabilidad en base al puntaje
    """
    match puntaje:
        case 2 | 3:
            return "Regular"
        case 4:
            return "Saludables"
        case 5:
            return "Buena"
        case _:
            return "Insuficiente"
        
def add_condicion_de_habitabilidad(hogar):
    """
    Asigna la condición de habitabilidad de un hogar en función de varios factores relacionados con el baño y el piso.
    
    Args: Llega como parametro el dataset de hogares, este se modifica en el output

    """
    insuficientes = 0
    suficientes = 0
    # Si no tiene baño considero que suma 4 puntos de insuficiencia asegurando que es una vivienda en condiciones insuficientes
    if hogar['IV8'] == '2': # 1 = si, 2 = no
        insuficientes += 4
    else:
        suficientes += 1
        # Si tiene el baño en el interior de la vivienda suma 1 punto de suficiencia
        if hogar['IV9'] == '1': # 1 = dentro de la vivienda, 2 = fuera de la vivienda pero dentro del terreno, 3 = fuera del terreno
            suficientes += 1
        else:
            insuficientes += 1
        # Si tiene cadena suma 1 punto de suficiencia
        if hogar['IV10'] == '1': # 1 =  inodoro con botón / mochila /cadena y arrastre de agua, 2 = inodoro sin botón / cadena y con arrastre de agua (a balde), 3 = sin arrastre
            suficientes += 1
        else:
            insuficientes += 1
        # Si el desague es un hoyo/excavacion en la tierra suma 1 punto de insuficiencia
        if hogar['IV11'] == '4': # 1 = cloaca, 2 = camara septica y pozo ciego, 3 = pozo ciego, 4 = hoyo/excavacion
            insuficientes += 1
        else:
            suficientes += 1
    # Si tiene piso de ladrillo suelto y tierra suma un punto de insifuciencia
    if hogar['IV3'] == '3': # 1 = ceramica/baldosa/madera/ceramica/alfombra, 2 = cemento/ladrillo fijo, 3 = ladrillo suelto y tierra
        insuficientes += 1
    else:
        suficientes += 1
    # Calculo la condicion
    condicion = calculate_condition(suficientes - insuficientes)
    hogar['CONDICION_DE_HABITABILIDAD'] = condicion

