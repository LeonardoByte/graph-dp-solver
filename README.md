# Resolutor de Programación Dinámica en Grafos

Este proyecto es una aplicación de escritorio interactiva desarrollada en **Python 3** y **Tkinter** que permite resolver problemas de optimización de caminos en grafos (Maximizar Ganancia o Minimizar Costo) utilizando algoritmos de **Programación Dinámica** de manera visual y didáctica.

La aplicación adopta una arquitectura estructurada **MVC (Modelo-Vista-Controlador)** bajo el Paradigma Orientado a Objetos (POO).

---

## Estructura del Proyecto

```text
dinamic_graph_solver/
│
├── .gitignore               # Archivos y carpetas ignorados por Git (ej: venv/)
├── README.md                # Documentación del proyecto (Este archivo)
├── requirements.txt         # Dependencias del proyecto (librería estándar)
├── main.py                  # Punto de entrada de la aplicación
│
├── core/                    # CAPA MODELO (Lógica matemática y algoritmos)
│   ├── __init__.py
│   ├── graph.py             # Clases Node, Edge y Graph (reindexación y validaciones)
│   └── dp_solver.py         # Algoritmos DP Regresivo (por etapas) y Progresivo (topológico)
│
├── gui/                     # CAPA VISTA (Interfaces de usuario con Tkinter)
│   ├── __init__.py
│   ├── main_window.py       # Ventana principal y layout 40-60
│   ├── canvas_panel.py      # Panel del Canvas interactivo con scrollbars y snapping
│   ├── text_panel.py        # Editor de texto plano con scrollbars independientes
│   ├── history_panel.py     # Lista del historial de grafos guardados
│   └── resolution_panels.py # Paneles didácticos con scroll bidireccional para tablas y pasos
│
├── controllers/             # CAPA CONTROLADOR (Orquestador principal)
│   ├── __init__.py
│   └── graph_controller.py  # Manejo de eventos, persistencia y parseo de datos
│
└── tests/                   # PRUEBAS UNITARIAS
    ├── __init__.py
    └── test_dp_solver.py    # Suite de tests unitarios para los motores de resolución
```

---

## Características Principales

### 1. Interfaz y Layout 40-60 Estricto
La pantalla principal se divide en dos secciones permanentes:
* **Izquierda (40% de ancho):** El Canvas interactivo del grafo, siempre visible.
* **Derecha (60% de ancho):** Contenedor de las vistas dinámicas de navegación intercambiables (Editor de Texto, Historial de Archivos, Tablas de Resolución Regresiva y Pasos de Resolución Progresiva).

### 2. Scrollbars Independientes y Bidireccionales
* El lienzo del Canvas soporta una resolución virtual fija de `1200x800` con barras de desplazamiento vertical y horizontal, previniendo que el grafo se distorsione al redimensionar la ventana.
* El editor de texto y las vistas de resolución utilizan scrollbars bidimensionales independientes para que las tablas anchas y largas se visualicen perfectamente sin solapamiento ni recortes.

### 3. Ingreso Visual Interactivo (Canvas)
* **Creación de Nodos:** Clic izquierdo sobre un espacio vacío del canvas coloca un nodo en el centro (snapping) de la etapa/columna física más cercana.
* **Reindexación Automática:** Al crear o mover nodos en el eje X, el sistema los numera secuencialmente de izquierda a derecha de $1$ a $N$ (sin huecos). El nodo $1$ (Origen) es el de más a la izquierda y es verde, y el nodo $N$ (Destino) es el de más a la derecha y es rojo.
* **Conexión de Aristas:** Clic en un nodo Origen A y clic en un nodo Destino B (con la restricción de que $A$ esté a la izquierda de $B$) abre un diálogo flotante solicitando el peso.
* **Arrastre y Movimiento:** Arrastre de nodos libremente en el eje Y y con ajuste magnético en las columnas en el eje X.
* **Eliminación:** Doble clic sobre un nodo remueve el elemento y sus aristas, reindexando todo de forma inmediata.

### 4. Ingreso por Texto Plano
* Panel que recibe una entrada con formato estricto: `Origen Destino Peso`.
* Al pulsar **"Validar y Cargar Grafo"**, se parsea la información, se comprueba que no contenga ciclos ni aristas de derecha a izquierda y se calcula de forma automática un renderizado visual simétrico, centrado y ordenado por columnas en el Canvas.

### 5. Historial de Grafos
* Permite guardar el grafo actual en la carpeta local `historial_grafos/` mediante archivos `.txt` bajo nombres únicos que registran fecha y hora.
* Desde el panel se pueden cargar directamente en el editor o eliminarlos permanentemente.

### 6. Métodos de Resolución Didácticos
* **Programación Dinámica Regresiva:** Resuelve de atrás hacia adelante (de destino a origen). Divide el grafo en etapas y estados calculando el óptimo acumulado. Muestra dinámicamente las matrices de transición de cada etapa y resalta en verde la celda óptima.
* **Programación Dinámica Progresiva:** Resuelve de adelante hacia atrás (en sentido de las flechas) basándose en orden topológico. Detalla la pregunta proactiva en cada nodo y el paso a paso del vector lineal `caminos[]`.
* **Visualización de Ruta:** Resalta en color azul eléctrico y con mayor grosor el camino óptimo directamente en el Canvas interactivo izquierdo tras resolver.

---

## Requisitos e Instalación

### Configuración del Entorno Virtual (Recomendado)
```bash
# 1. Clonar o acceder al directorio del proyecto
cd dinamic_graph_solver/

# 2. Inicializar repositorio Git
git init

# 3. Crear entorno virtual
python -m venv venv

# 4. Activar el entorno virtual
# En Windows (PowerShell):
.\venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate
```

---

## Instrucciones de Uso

### Ejecutar la Aplicación
Inicie el software ejecutando:
```bash
python main.py
```

### Ejecutar la Suite de Pruebas Unitarias
Para validar que el resolvedor calcula de forma óptima los costos y rutas bajo los motores regresivo y progresivo (Max/Min):
```bash
python -m unittest tests/test_dp_solver.py
```
