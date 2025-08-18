# Deliverie1-Artificial-Intelligence-


## Participantes
- Sebastian Andres Medina Cabezas
- Samuel DeOssa

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


# Un Enfoque Inteligente para la Planificación del Tiempo  

Mi problema consiste en crear un horario semanal optimizado. Tengo una serie de actividades fijas, como la universidad y los entrenamientos de fútbol, que no puedo mover. Además, necesito incluir actividades flexibles como dormir, estudiar y hacer ejercicio, que tienen requisitos específicos: dormir un número determinado de horas, ir al gimnasio en bloques de 1 hora dos veces por semana, y estudiar un total de horas. El desafío es encontrar la mejor manera de encajar estas actividades flexibles alrededor de las fijas para generar un horario que cumpla con todos los requisitos y, al mismo tiempo, sea lógico y me permita tener un buen equilibrio entre mis responsabilidades y mi bienestar.  

---

## ¿Planificación o Programación?  

Este es un problema de planificación, y más específicamente, de asignación de recursos.  

Se trata de planificación porque la tarea principal es determinar qué hacer y cuándo. No solo estamos ordenando una secuencia de tareas predefinidas, sino que estamos decidiendo cuántas horas dedicar a cada actividad flexible (estudio, sueño, etc.) y en qué momentos de la semana ubicarlas para lograr los objetivos deseados. El algoritmo tiene la libertad de colocar estas actividades en cualquier momento disponible, buscando la mejor distribución posible.  

---

## ¿Por qué un algoritmo genético es la elección adecuada?  

Un algoritmo genético (GA) es ideal para este problema por varias razones:  

1. **Es un problema de optimización complejo:**  
   El espacio de soluciones es inmenso. Cada uno de los 7 días tiene 48 bloques de 30 minutos, y en cada uno de esos 336 bloques se puede asignar una de varias actividades. Enumerar todas las combinaciones posibles es inviable. Un GA nos permite buscar una solución de alta calidad sin tener que explorar cada opción.  

2. **Permite múltiples criterios de evaluación:**  
   La calidad de un horario no depende de una sola métrica. No es solo “dormir 8 horas”. También importa que el sueño sea continuo y nocturno, que el gimnasio sea en bloques de 1 hora, que no haya conflictos, y que el estudio esté distribuido. Un GA nos permite combinar todos estos criterios en una sola función de *fitness*.  

3. **Se adapta a restricciones y objetivos:**  
   Podemos codificar fácilmente las restricciones de las actividades fijas y los objetivos de las actividades flexibles. Mutación y cruce, junto con una función de *fitness* robusta, hacen que las soluciones que violen restricciones sean penalizadas y descartadas.  

4. **Puede encontrar soluciones creativas:**  
   Un GA explora combinaciones que un enfoque determinista no consideraría, como dividir el estudio en bloques cortos y efectivos en lugar de largas sesiones.  

---

## Representación de la Solución (Cromosoma) y Evaluación (Fitness)  

**Cromosoma**  
Una posible solución se representa como un vector de 336 elementos (7 días × 48 bloques). Cada elemento es una actividad:  
- “Universidad”  
- “Entrenamiento”  
- “Sueño”  
- “Estudio”  
- “Gym”  
- “Social”  
- “ ” (vacío)  

**Función de Evaluación (Fitness)**  
El puntaje de un horario se basa en **premios y penalizaciones**:  

- **Premios:**  
  - Sueño continuo 6–8h, especialmente nocturno.  
  - Gimnasio exactamente 2 veces/semana, en bloques de 1h.  
  - Cumplir total de horas de estudio.  
  - Tiempo social.  

- **Penalizaciones:**  
  - Conflictos con actividades fijas.  
  - Sueño fragmentado.  
  - Gimnasio con duración incorrecta.  
  - No cumplir mínimos de sueño o gimnasio.  

El puntaje final es la suma de premios y penalizaciones.  

---

## Elementos del Algoritmo Genético  

Población Inicial: Generamos una población de horarios aleatorios o, en nuestro caso, sembrados inteligentemente. Cada individuo de la población es un cromosoma (un horario de 336 slots). Al comenzar con horarios que ya tienen el sueño y el gimnasio colocados de manera lógica, le damos un buen punto de partida al algoritmo, lo que acelera la convergencia hacia una buena solución.

Selección: Usamos la selección por torneo. De la población actual, elegimos aleatoriamente un pequeño grupo de individuos (por ejemplo, 20 o 30) y seleccionamos al que tiene el mejor puntaje de fitness. Repetimos este proceso para elegir los "padres" de la siguiente generación. Esto asegura que los individuos más aptos tengan más probabilidades de ser elegidos para reproducirse. También se añade una porción de la élite (los mejores individuos) para que sobrevivan directamente a la siguiente generación, garantizando que el mejor progreso no se pierda.

Cruce (Crossover): Los dos padres seleccionados se combinan para crear un "hijo". Usamos un cruce de un punto. Se elige un punto de corte aleatorio en el cromosoma, y el hijo se crea tomando la primera parte del primer padre y la segunda parte del segundo padre. Esto permite que los "genes" (segmentos de horarios) de los mejores individuos se combinen, creando nuevas soluciones potencialmente superiores.

Mutación: Después del cruce, el nuevo individuo (el hijo) puede sufrir una mutación. Con una pequeña probabilidad, un slot aleatorio en el cromosoma cambia de actividad flexible. Nuestra mutación es "inteligente": si un slot está en un horario nocturno, la probabilidad de que se convierta en "Sueño" es mayor. Esta mutación evita que la población se estanque en soluciones subóptimas y le permite al algoritmo explorar nuevas áreas del espacio de soluciones. La mutación también protege los slots de gimnasio apropiados para no deshacer el progreso.

Criterio de Parada: El algoritmo se detiene después de un número fijo de generaciones (en nuestro caso, 400). En cada generación, el algoritmo produce una nueva población y evalúa el progreso. El criterio de parada garantiza que la búsqueda no continúe indefinidamente y que el proceso termine en un tiempo razonable, devolviendo el mejor horario encontrado hasta ese momento.



