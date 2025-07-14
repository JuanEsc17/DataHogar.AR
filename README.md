# 📊 Grupo 5 - Trabajo Práctico Integrador

DataHogar.AR - Encuesta Permanente de Hogares (EPH)

Visualización y análisis de datos utilizando Python, Jupyter Notebook y Streamlit. 

## 👥 Integrantes
- Malena Carrasco Dattoli 24568/9
- Juan Escudero 22948/9
- Alejandra Melisa López 25404/3
- Catalina Gatica Fraysse 23667/7
- Joaquín Nicolas Zaragoza Armendariz 22965/1

# 🧠 Descripción del proyecto

Este proyecto utiliza Streamlit para visualizar y analizar datos provenientes de encuestas de hogares e individuos. El objetivo es explorar distintos indicadores sociales y económicos a través de una interfaz visual.

## 📦 Requisitos

Antes de comenzar, asegurate de tener instalado:

- [Python Python 3.12.9+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [Git (opcional pero recomendado)](https://github.com/git-guides/install-git)
- Jupyter Notebook
- Streamlit

## ⚙️ Instalación
1. Instalar [Python 3.12.9](https://www.python.org/downloads/release/python-3129/)

2. Descargar o clonar el repositorio (si estás usando Git):
```bash
  git clone https://gitlab.catedras.linti.unlp.edu.ar/python-2025/proyectos/grupo05/code.git
  cd code
```
3. Instalar y activar entorno virtual: 
```bash
  python -m venv venv
```
  Para windows:
  ```bash
  venv\Scripts\activate.bat
  ```
  Para linux:
  ```bash
  source ./venv/bin/activate
  ```
4. Una vez instalado Python y Git podes instalar las dependencias de manera automática corriendo el siguiente código en la terminal, posicionandóse en la carpeta correspondiente.
```bash
  python -m pip install -r requirements.txt
```
Este comando instala las dependencias especificadas en `requirements.txt` para este proyecto para una mejor compatibilidad.

5. Instalación manual (si no usás el archivo de requirements):
  ```bash
  pip install jupyterlab
  pip install streamlit
  pip install pandas
  pip install matplotlib
  pip install folium
  pip install streamlit-folium
```

## 🚀 Ejecución
### Opcion 1: Desde Jupyter Notebook
En la consola de Windows, ejecutá el siguiente comando:
```bash
  jupyter notebook
```
Al ejecutarse, se abrirá una nueva pantalla en tu navegador predeterminado. En esa pestaña, podrás seleccionar el archivo `main.ipynb` del proyecto, clickeando "run" se ejecutará el código y se mostrará en pantalla las funcionalidades del mismo.

### Opcion 2: Visual Studio Code 

Posicionandóse sobre el archivo y seleccionando la versión de Python que utilices (Ctrl+Shift+P → Python: Select Interpreter), podrás ejecutar la celda seleccionada haciendo click en el botón de Play arriba a la izquierda, o presionando el botón Ctrl+Alt+Enter.

## Opcion 3: Streamlit
Podés correr la app con:
Situarse en la carpeta correspondiente a Streamlit. Una vez situado en esa carpeta, se puede ejecutar inicio:
```bash
  cd streamlit
  streamlit run 01_inicio.py
```

🌐 Esto abrirá la app en tu navegador en http://localhost:8501.

## 📁 Estructura del Proyecto:
```bash
├── .vscode/                         # Configuraciones específicas de VSCode
│
├── files/                          # Archivos de entrada originales (.txt) provenientes de EPH
│
├── files_out/                      
│   ├── usu_hogares.csv             # Datos de hogares
│   ├── usu_individuales.csv        # Datos de personas 
│
├── notebooks/                      # Jupyter Notebook del proyecto
│   └── main.ipynb                  # Notebook principal que llama a las funciones de la Sección A y Sección B
│
├── src/                            # Código fuente del proyecto
│   ├── functions/                  # Carpeta de funciones generales reutilizables
│   │   ├── __init__.py            
│   │   ├── functions_A.py          # Funciones de la Sección A: transformación de datos
│   │   ├── functions_B.py          # Funciones de la Sección B: análisis de datos
│   │   ├── functions_comunes.py    # Funciones compartidas entre módulos
│   │   ├── functions_st.py         # Funciones de la Sección Streamlit
│   │   └── utils/
│   │       └──constantes.py       # Contiene funciones helpers, validaciones, etc.
│   └── functions_streamlit/        # Funciones específicas de cada página de Streamlit
│       ├── __init__.py
│       ├── functions_actividad_y_empleo.py      # Funciones para la página de Actividad y Empleo
│       ├── functions_caracteristicas_demo.py    # Funciones para la página Características Demográficas
│       ├── functions_carga_datos.py             # Funciones para la página Carga de datos
│       ├── functions_educacion.py               # Funciones para la página Educación
│       └── functions_vivienda.py                # Funciones para la página Características de Vivienda
│
├── streamlit/                      # Estructura del Frontend de la aplicación
│   ├── pages/                      # Páginas visibles en la app de Streamlit
│   │   ├── 02_Carga_de_datos.py                   # Página de Actividad y Empleo
│   │   ├── 03_Características_demográficas.py     # Página de Características de Vivienda
│   │   ├── 04_Características_de_la_vivienda      # Página de Características Demográficas
│   │   ├── 05_Actividad_y_empleo                  # Página de Carga de datos
│   │   ├── 06_Educación.py                        # Página de Educación
│   │   ├── 07_Ingresos.py                         # Página de Ingresos
│   └── 01_inicio.py                 # Página de Inicio de la aplicación
│
├── venv/                            # Entorno virtual de Python
│
├── .gitignore                       # Ignora carpetas como venv/, __pycache__, etc.
├── LICENSE                          # Licencia del proyecto
├── README.md                    
└── requirements.txt                 # Lista de dependencias a instalar con pip
```