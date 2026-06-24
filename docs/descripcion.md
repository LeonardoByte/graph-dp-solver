# Especificación de Proyecto: Resolutor de Programación Dinámica en Grafos

Este documento contiene las especificaciones técnicas, la arquitectura de software y los pasos de inicialización para el desarrollo de una aplicación de escritorio que resuelve problemas de optimización en grafos (Maximizar/Minimizar caminos entre un nodo A y un nodo B) mediante **Programación Dinámica**, utilizando **Python 3** y **Tkinter** para la interfaz gráfica.

---

## 1. Configuración Inicial del Entorno

Antes de comenzar con el desarrollo del código, se deben ejecutar los siguientes comandos en la terminal para preparar el entorno de trabajo:

```bash
# 1. Inicializar el repositorio Git
git init

# 2. Crear el entorno virtual (venv)
python -m venv venv

# 3. Activar el entorno virtual
venv\Scripts\activate

# 4. Crear archivo de dependencias iniciales
echo "# Dependencias del proyecto" > requirements.txt

```

---

## 2. Arquitectura y Estructura de Carpetas

Para garantizar la escalabilidad, el mantenimiento y la separación de responsabilidades, se adoptará una arquitectura **MVC (Modelo-Vista-Controlador)** adaptada a aplicaciones de escritorio, implementada bajo el **Paradigma Orientado a Objetos (POO)**.

### Estructura del Proyecto:

```text
dinamic_graph_solver/
│
├── .gitignore               # Archivos y carpetas a ignorar por Git (ej: venv/)
├── README.md                # Documentación del proyecto
├── requirements.txt         # Dependencias del proyecto
├── main.py                  # Punto de entrada de la aplicación
│
├── docs/                    # Documentación del proyecto
│   ├── Enunciado.png        # Enunciado base del problema
│   └── descripcion.md       # Descripción del proyecto y de cada componente (Este archivo)
│
├── core/                    # CAPA MODELO (Lógica de negocio y algoritmos)
│   ├── __init__.py
│   ├── graph.py             # Clases Nodo, Arista y Grafo
│   └── dp_solver.py         # Algoritmo de Programación Dinámica (Min/Max)
│
├── gui/                     # CAPA VISTA (Interfaces de usuario con Tkinter)
│   ├── __init__.py
│   ├── main_window.py       # Ventana principal y layouts
│   ├── canvas_panel.py      # Panel interactivo para arrastrar/dibujar nodos
│   └── text_panel.py        # Panel de ingreso de texto y validación
│
└── controllers/             # CAPA CONTROLADOR (Orquestador entre Modelo y Vista)
    ├── __init__.py
    └── graph_controller.py  # Manejador de eventos, carga de datos y cálculo

```

---

## 3. Requerimientos Funcionales y Restricciones

### 3.1. Interfaz Gráfica (GUI)

* Debe ser desarrollada exclusivamente utilizando la librería nativa **Tkinter** (se permite el uso de `tkinter.ttk` para mejorar estilos).

### 3.2. Restricciones del Grafo

* **Identificación:** Los nodos se identificarán **estrictamente con índices numéricos enteros a partir del 1** (1, 2, 3...), descartando el uso de letras.

### 3.3. Modos de Operación (Adaptabilidad)

El sistema debe permitir al usuario seleccionar el objetivo de la optimización:

1. **Maximizar:** Encontrar la ruta con la mayor ganancia/costo acumulado (ej. Problema de la diligencia).
2. **Minimizar:** Encontrar la ruta con el menor costo/distancia acumulada (ej. Ruta crítica o camino mínimo).

### 3.4. Métodos de Ingreso de Datos

#### Opción 1: Interfaz Visual e Interactiva (Drag & Drop)

* Un panel (Canvas) donde el usuario pueda hacer clic para crear un nodo (generando automáticamente el índice correspondiente).
* Permitir arrastrar los nodos para reacomodar visualmente el grafo.
* Permitir conectar nodos mediante aristas e ingresar el peso de las mismas a través de un cuadro de diálogo flotante o campo dedicado.

#### Opción 2: Ingreso por Texto Plano

* Un área de texto (`tk.Text`) que reciba la definición del grafo línea por línea con el siguiente formato estricto:
```text
Indice_nodo_inicio Indice_nodo_destino valor_peso_arista
```

*Ejemplo de entrada:*
```text
1 2 4
1 3 3
2 4 7
3 4 2
```

### 3.5. Validaciones Requeridas (Opción 2)

Al momento de hacer clic en un botón "Guardar/Cargar Grafo", el sistema debe validar:

* Que cada línea contenga exactamente 3 valores numéricos separados por espacios.
* Que los índices de los nodos sean enteros positivos.
* Que no existan definiciones duplicadas para una misma arista dirigida.
* **Visualización:** Si el texto es válido, el grafo debe **dibujarse automáticamente** en el panel interactivo de la *Opción 1* para que el usuario corrobore la estructura de forma visual.

### 3.6. Criterio de selección del nodo inicial y final del grafo

Al cargar el grafo para ejecutar el algoritmo de programación dinámica, el nodo de inicio será el que tenga el índice 1 y el nodo final será el que tenga el índice más alto. Los nodos se identificarán con un color diferente para que el usuario sepa cuál es el nodo inicial y cuál es el nodo final.

### 3.7. Historial de los grafos ingresados

Debe existir un historial de los grafos ingresados, para que el usuario pueda ver los grafos que ha ingresado y pueda seleccionar uno para ejecutar el algoritmo de programación dinámica. Los grafos se deben guardar en archivos .txt en una carpeta llamada "historial_grafos". Cada grafo debe tener un nombre único y debe ser guardado con la fecha y hora en que fue creado. Deberan existir botones "Guardar Grafo" y "Cargar Grafo" para poder guardar y cargar los grafos. Debe terner opciones para "Resolver grafo", "Editar grafo" y "Eliminar grafo".
### 3.8. Métodos de resolución

Los métodos de resolución deben ser capaces de guardar las iteraciones de cada paso para la posterior presentación en la interfaz gráfica; como este es un código didáctico, es necesaria la presentación de las iteraciones/pasos de los algoritmos.

1. **Programación Dinámica Regresiva:**
Resuelve el problema de atrás hacia adelante (de derecha a izquierda). Divide el grafo en niveles verticales llamados Etapas y a cada nodo lo llama Estado. El objetivo es calcular el costo óptimo desde cualquier nodo hasta el destino final.

* Estructura de sus iteraciones: Obliga a construir una tabla bidimensional independiente por cada etapa (columna). En cada tabla, los nodos de la columna actual se colocan como filas y los nodos de la siguiente columna como columnas de la tabla. Cada celda interna debe mostrar la suma explícita de: [Valor de la flecha actual] + [Óptimo acumulado guardado en la tabla de la etapa anterior]. Al final de cada tabla, se evalúan todas las alternativas de la fila para elegir y anotar un único valor y decisión óptima.

2. **Programación Dinámica Progresiva:**
Resuelve el problema de adelante hacia atrás (de izquierda a derecha) en el sentido natural de las flechas. En lugar de mirar hacia el destino, calcula el costo óptimo acumulado desde el origen hasta cada nodo intermedio del camino.

* Estructura de sus iteraciones: A diferencia del método regresivo, aquí no existen tablas por columnas ni divisiones artificiales de etapas. El algoritmo prescinde por completo de matrices bidimensionales y se posiciona directamente en los nodos siguiendo un estricto orden de indexación (creación del nodo). Para cada nodo en el que se para, realiza una única pregunta proactiva: «¿Cuál es el camino óptimo desde el origen hasta mí mismo?». Revisa a todos sus nodos padres directos, calcula cuál le hereda el mejor costo acumulado y guarda ese único valor directamente en un arreglo lineal de tamaño [n][2] (caminos[nodo] = {padre, peso_acumulado}). La única condición operativa es que los nodos estén indexados en orden (orden topológico de izquierda a derecha) para asegurar que ningún nodo sea procesado antes de que sus padres ya tengan su costo definitivo calculado.
---

## 4. Requerimientos Técnicos de Código (POO)

* **Clase `Graph` / `Node` / `Edge`:** El grafo interno no debe ser un simple diccionario; debe manejarse mediante objetos que contengan los estados y métodos de adyacencia.
* **Clase `DPSolver`:** Debe encapsular los métodos de resolución de programación dinámica por etapas, aislando por completo la matemática del grafo de los componentes visuales.
* **Manejo de Errores:** Cualquier dato corrupto en la Opción 2 o ciclo inválido en el grafo debe lanzar excepciones controladas que se muestren al usuario mediante `tkinter.messagebox.onerror`.
