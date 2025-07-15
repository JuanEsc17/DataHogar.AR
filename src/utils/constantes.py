from pathlib import Path

PROJECT_PATH = Path(__file__).parent.parent.parent # Path al directorio raíz
DATA_PATH = PROJECT_PATH / "files"
DATA_OUT_PATH = PROJECT_PATH / "files_out"

# Patrones de entrada
INPUT_PATTERN_INDIVIDUOS = "usu_individual_*.txt"
INPUT_PATTERN_HOGARES = "usu_hogar_*.txt"

# Archivos de salida
OUTPUT_FILENAME_INDIVIDUOS = "usu_individuales.csv"
OUTPUT_FILENAME_HOGARES = "usu_hogares.csv"

# Sección B - Ejercicio 06
AGLOMERADO_ID_A_NOMBRE = {
    '2': 'Gran La Plata',
    '3': 'Bahía Blanca - Cerri',
    '4': 'Gran Rosario',
    '5': 'Gran Santa Fé', 
    '6': 'Gran Paraná',
    '7': 'Posadas',
    '8': 'Gran Resistencia',
    '9': 'Comodoro Rivadavia - Rada Tilly',
    '10': 'Gran Mendoza',
    '12': 'Corrientes',
    '13': 'Gran Córdoba',
    '14': 'Concordia',
    '15': 'Formosa',
    '17': 'Neuquén – Plottier',
    '18': 'Santiago del Estero - La Banda',
    '19': 'Jujuy - Palpalá',
    '20': 'Río Gallegos',
    '22': 'Gran Catamarca',
    '23': 'Gran Salta',
    '25': 'La Rioja',
    '26': 'Gran San Luis',
    '27': 'Gran San Juan',
    '29': 'Gran Tucumán - Tafí Viejo',
    '30': 'Santa Rosa – Toay',
    '31': 'Ushuaia - Río Grande',
    '32': 'Ciudad Autónoma de Buenos Aires',
    '33': 'Partidos del GBA',
    '34': 'Mar del Plata',
    '36': 'Río Cuarto',
    '38': 'San Nicolás – Villa Constitución',
    '91': 'Rawson – Trelew',
    '93': 'Viedma – Carmen de Patagones'
}
#Seccion B - Ejercicio 8
REGION_ID_A_NOMBRE = {
    '1': 'Gran Buenos Aires',
    '40': 'Noroeste',
    '41': 'Noreste',
    '42': 'Cuyo',
    '43': 'Pampeana',
    '44': 'Patagonia'
} 
#Seccion B - Ejercicio 9
NIVEL_EDUCATIVO_ID_A_NOMBRE = {
    '1':  'Primario incompleto (incluye educación especial)',
    '2': 'Primario completo',
    '3': 'Secundario incompleto',
    '4': 'Secundario completo',
    '5': 'Superior universitario incompleto',
    '6': 'Superior universitario completo',
    '7': 'Sin instrucción',
    '9': 'Ns/Nr'
}
#Parte 2 - Pagina 6
CH12_ID_A_NOMBRE = {
    0: 'Sin instrucción',
    1: 'Jardín/preescolar',
    2: 'Primario',
    3: 'EGB',
    4: 'Secundario',
    5: 'Polimodal',
    6: 'Terciario',
    7: 'Universitario',
    8: 'Posgrado universitario',
    9: ' Educación especial (discapacitado)',
    99: 'Ns/Nr'
}
INTERVALOS_ETARIOS_EDUCACION = [
    "20 a 30",
    "30 a 40",
    "40 a 50",
    "50 a 60",
    "Más de 60",
    "Todos"
]
PISO_ID_A_NOMBRE = {
    1: "Mosaico / Baldosa / Madera / Cerámica / Alfombra",
    2: "Cemento / Ladrillo fino",
    3: "Ladrillo Suelto / Tierra"
}

TENENCIA_ID_A_NOMBRE = {
    1: "Propietario de la vivienda y el terreno",
    2: "Propietario de la vivienda solamente",
    3: "Inquilino / arrendatario",
    4: "Ocupante por pago de impuestos",
    5: "Ocupante en relación de dependencia",
    6: "Ocupante gratuito (con permiso)",
    7: "Ocupante de hecho (sin permiso)",
    8: "Está en sucesión"
}

VIVIENDAS_ID_A_NOMBRE = {
    1: "Casa",
    2: "Departamento",
    3: "Pieza de inquilinato",
    4: "Pieza en hotel/pensión",
    5: "Local no construido para habitación"
}