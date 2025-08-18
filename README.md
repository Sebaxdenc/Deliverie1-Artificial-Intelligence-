# Deliverie1-Artificial-Intelligence-


## Participantes
- Sebastian Andres Medina Cabezas
- Samuel Deossa

## Problema 1

Desarrollo de un agente de búsqueda para navegación de un dron en una ciudad modelada como grafo.

### Resumen del problema
- Planificar la ruta minimizando el costo total = distancia euclidiana + λ_w · viento por arista.
- Requisitos: representar el espacio de estados, hallar el camino inicio→meta, mostrar la exploración paso a paso y reportar camino, número de nodos explorados y tiempo de ejecución. Comparar A* vs BFS. Considerar calles ortogonales/diagonales y algunas restricciones.

### Solución implementada
- Modelo CityGraph: coordenadas por nodo; aristas no dirigidas con penalización de viento; costo de arista = euclidiana + λ_w · viento; heurística h = euclidiana (admisible/consistente).
- Algoritmos: A* con cola de prioridad y trazas (verbose), BFS no ponderado; reconstrucción de camino y cálculo del costo real del camino.
- Demo: malla 5×4 (A0..E3); calles restringidas y mapa de vientos (con claves frozenset); atajos diagonales; aristas agregadas de forma explícita.
- Las coordenadas se crearon de tal manera que la distancia horizontal entre cualesquiera dos nodos va a ser de 1, y la distancia diagonal sera la raiz cuadrada de 2

     ![grafo de la ciudad](imgs/grafo_agente_busqueda.png)

### Tecnologías y librerías
- Python 3
- Librerías estándar: math (hypot), heapq, time, dataclasses, typing, collections.deque
- Estructuras: dict para coordenadas/adyacencia; frozenset como clave no dirigida para restricted y wind_map
- Entorno: VS Code

## Problema 2
# Generador de Horarios Inteligente  

El problema central es **generar un horario semanal óptimo** que equilibre las actividades fijas y las necesidades personales de un estudiante universitario-deportista.  
Esto incluye las clases de la universidad y los entrenamientos, con actividades flexibles como dormir, ir al gimnasio y estudiar.  

---
## Hecho por 
- Sebastian Andres Medina Cabezas
- Samuel Deossa

## Herramientas y participantes del código

- **Agente**: El **algoritmo genético (AG)**, que es el "cerebro" del sistema. Su objetivo es encontrar la mejor solución para el horario.  
- **Individuos**: Cada "horario" creado por el algoritmo es un individuo.  
  - Un horario se representa como una lista o vector con **336 bloques de 30 minutos** (48 bloques por día × 7 días).  
  - Cada bloque se llena con una actividad específica.  
- **Entorno**: Las **reglas y restricciones** que guían al algoritmo.  
  - Incluyen las horas de clase fijas, entrenamientos y partidos.  
  - La función de *fitness* evalúa qué tan bien se cumplen estas reglas y qué tan balanceado es el horario.  

---

## Tecnologías Utilizadas  

- **Algoritmo Genético (AG)**  
  - Técnica de **inteligencia artificial** que imita la evolución natural.  
  - Genera una población de horarios aleatorios y, mediante selección, cruce y mutación, produce nuevas generaciones cada vez más optimizadas.  

- **Python**  
  - Lenguaje de programación principal del sistema.  
  - Su simplicidad y ecosistema de librerías lo hacen ideal para IA y manejo de datos.  

- **Pandas**  
  - Librería de Python para **gestión y visualización de datos**.  
  - Permite manejar el horario como un DataFrame y verlo en formato de tabla clara.  

- **openpyxl**  
  - Librería de Python para **exportar datos a Excel (`.xlsx`)**.  
  - Facilita guardar el horario generado y consultarlo de manera práctica.  

---


