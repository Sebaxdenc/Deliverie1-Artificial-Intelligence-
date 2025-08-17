"""
Agente de búsqueda para navegación de un dron en una ciudad modelada como grafo.

Espacio de estados:
- Estados: nodos del grafo (intersecciones/puntos de la ciudad)
- Acciones: moverse por aristas válidas (calles no restringidas)
- Modelo de transición: Result(vi, a) = vj si existe arista (vi, vj)
- Costo: c(vi, a, vj) = DistEuclidiana(vi, vj) + λ_w * Wind(vi, vj)
- Heurística h(s): Distancia euclidiana desde s a la meta (admisible/consistente)

Salida:
- Camino óptimo encontrado
- Número de nodos explorados (expansiones)
- Tiempo de ejecución
- Trazas paso a paso de la exploración (verbose=True)
"""
import math
import heapq
import time
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional, Iterable


Coord = Tuple[float, float]


@dataclass
class Edge:
    """Arista con penalización de viento (no almacena costo base, que es euclidiano)."""
    u: str
    v: str
    wind: float = 0.0  # penalización no negativa


class CityGraph:
    def __init__(self, coords: Dict[str, Coord], lambda_w: float = 1.0, undirected: bool = True) -> None:
        self.coords: Dict[str, Coord] = coords
        self.lambda_w: float = float(lambda_w)
        self.undirected: bool = undirected
        # adjacency[u][v] = wind_penalty
        self.adjacency: Dict[str, Dict[str, float]] = {n: {} for n in coords}

    def add_edge(self, u: str, v: str, wind: float = 0.0) -> None:
        if u not in self.coords or v not in self.coords:
            raise ValueError(f"Nodo inexistente en coords: {u} o {v}")
        if wind < 0:
            raise ValueError("La penalización de viento debe ser no negativa")
        self.adjacency[u][v] = float(wind)
        if self.undirected:
            self.adjacency[v][u] = float(wind)

    def neighbors(self, u: str) -> Iterable[str]:
        return self.adjacency[u].keys()

    def euclidean(self, a: str, b: str) -> float:
        (x1, y1), (x2, y2) = self.coords[a], self.coords[b]
        return math.hypot(x1 - x2, y1 - y2)

    def cost(self, u: str, v: str) -> float:
        if v not in self.adjacency[u]:
            raise ValueError(f"Arista restringida o inexistente: {u}->{v}")
        base = self.euclidean(u, v)
        wind_penalty = self.adjacency[u][v]
        return base + self.lambda_w * wind_penalty

    def h(self, s: str, goal: str) -> float:
        # Heurística euclidiana (admisible al ignorar viento, consistente en grafos con costos no negativos)
        return self.euclidean(s, goal)


@dataclass
class SearchResult:
    path: List[str]
    cost: float
    explored: int
    runtime_sec: float
    expanded_order: List[str]


def reconstruct_path(came_from: Dict[str, str], start: str, goal: str) -> List[str]:
    path: List[str] = [goal]
    cur = goal
    while cur != start:
        cur = came_from[cur]
        path.append(cur)
    path.reverse()
    return path


def astar(
    graph: CityGraph,
    start: str,
    goal: str,
    verbose: bool = False,
) -> SearchResult:
    if start not in graph.coords or goal not in graph.coords:
        raise ValueError("El nodo inicial o meta no existe en el grafo")

    t0 = time.perf_counter()

    counter = 0  # desempate estable en heap por si dos nodos tienen el mismo f y g
    open_heap: List[Tuple[float, float, int, str]] = []  # (f, g, tie, node)
    g: Dict[str, float] = {start: 0.0}
    f0 = graph.h(start, goal)
    heapq.heappush(open_heap, (f0, 0.0, counter, start))

    came_from: Dict[str, str] = {}
    closed: set[str] = set()
    explored_count = 0
    expanded_order: List[str] = []

    if verbose:
        print(f"Inicio A*: start={start}, goal={goal}")

    while open_heap:
        f_cur, g_cur, _, u = heapq.heappop(open_heap)
        if u in closed:
            continue
        closed.add(u)
        explored_count += 1
        expanded_order.append(u)

        if verbose:
            h_u = graph.h(u, goal)
            print(f"Expandir: {u} | g={g_cur:.3f}, h={h_u:.3f}, f={f_cur:.3f}")

        if u == goal:
            path = reconstruct_path(came_from, start, goal) if goal in came_from or start == goal else [start]
            t1 = time.perf_counter()
            return SearchResult(path=path, cost=g_cur, explored=explored_count, runtime_sec=(t1 - t0), expanded_order=expanded_order)

        for v in graph.neighbors(u):
            if v in closed:
                continue
            tentative_g = g_cur + graph.cost(u, v)
            if tentative_g < g.get(v, math.inf):
                came_from[v] = u
                g[v] = tentative_g
                counter += 1
                f_v = tentative_g + graph.h(v, goal)
                heapq.heappush(open_heap, (f_v, tentative_g, counter, v))
                if verbose:
                    print(
                        f"  Actualizar vecino {v}: g={tentative_g:.3f}, h={graph.h(v, goal):.3f}, f={f_v:.3f} (padre={u})"
                    )
            elif verbose:
                # Mostrar cuando NO se mejora el mejor costo conocido (el if falla)
                print(
                    f"  Omitir vecino {v}: g_tent={tentative_g:.3f} >= g_mejor={g.get(v, math.inf):.3f} (padre actual de {v} = {came_from.get(v, '-')})"
                )

    # Sin solución
    t1 = time.perf_counter()
    if verbose:
        print("No se encontró camino.")
    return SearchResult(path=[], cost=math.inf, explored=explored_count, runtime_sec=(t1 - t0), expanded_order=expanded_order)


def path_total_cost(graph: CityGraph, path: List[str]) -> float:
    """Suma el costo real de un camino dado (usando cost del grafo)."""
    if not path or len(path) == 1:
        return 0.0
    total = 0.0
    for u, v in zip(path, path[1:]):
        total += graph.cost(u, v)
    return total


def bfs(
    graph: CityGraph,
    start: str,
    goal: str,
    verbose: bool = False,
) -> SearchResult:
    """Búsqueda en anchura (no ponderada). Reporta el costo real del camino hallado."""
    from collections import deque

    if start not in graph.coords or goal not in graph.coords:
        raise ValueError("El nodo inicial o meta no existe en el grafo")

    t0 = time.perf_counter()
    q = deque([start])
    visited: set[str] = {start}
    came_from: Dict[str, str] = {}
    explored_count = 0
    expanded_order: List[str] = []

    if verbose:
        print(f"Inicio BFS: start={start}, goal={goal}")

    while q:
        u = q.popleft()
        explored_count += 1
        expanded_order.append(u)
        if verbose:
            print(f"Expandir (BFS): {u}")

        if u == goal:
            path = reconstruct_path(came_from, start, goal) if start != goal else [start]
            t1 = time.perf_counter()
            return SearchResult(
                path=path,
                cost=path_total_cost(graph, path),
                explored=explored_count,
                runtime_sec=(t1 - t0),
                expanded_order=expanded_order,
            )

        for v in graph.neighbors(u):
            if v in visited:
                continue
            visited.add(v)
            came_from[v] = u
            q.append(v)
            if verbose:
                print(f"  Descubrir (BFS) {v} (padre={u})")

    t1 = time.perf_counter()
    if verbose:
        print("BFS: No se encontró camino.")
    return SearchResult(path=[], cost=math.inf, explored=explored_count, runtime_sec=(t1 - t0), expanded_order=expanded_order)


def demo(verbose: bool = True) -> None:
    """Ejemplo con grafo grande (malla 5x4), viento y calles restringidas. Compara BFS y A*."""
    # Construir una malla 5x4 (20 nodos): etiquetas tipo A0..E3
    W, H = 5, 4
    coords: Dict[str, Coord] = {}
    for y in range(H):
        for x in range(W):
            name = f"{chr(65 + x)}{y}"
            coords[name] = (float(x), float(y))

    # λ_w pondera la penalización de viento
    graph = CityGraph(coords, lambda_w=1.5, undirected=True)

    # Definir calles restringidas (no se agregan) y penalizaciones de viento en algunos tramos
    restricted = {
        frozenset({"B0", "B1"}),
        frozenset({"C1", "C2"}),
        frozenset({"D0", "D1"}),
        frozenset({"A2", "A3"}),
        frozenset({"E2", "E3"}),
    }
    wind_map: Dict[frozenset[str], float] = {
        frozenset({"B0", "C0"}): 0.7,
        frozenset({"C0", "D0"}): 1.0,
        frozenset({"B1", "B2"}): 0.5,
        frozenset({"C1", "D1"}): 1.2,
        frozenset({"D1", "D2"}): 0.8,
        frozenset({"A2", "B2"}): 0.3,
        frozenset({"C2", "C3"}): 1.5,
        frozenset({"D2", "E2"}): 0.9,
        frozenset({"E1", "E2"}): 0.6,
        frozenset({"B2", "C2"}): 0.4,
        frozenset({"B3", "C3"}): 1.1,
    }

    def wind(u: str, v: str) -> float:
        return wind_map.get(frozenset({u, v}), 0.0)

    # Agregar calles ortogonales (sin bucles), omitiendo las restringidas
    # Horizontales fila 0
    graph.add_edge("A0", "B0", wind=wind("A0", "B0"))
    graph.add_edge("B0", "C0", wind=wind("B0", "C0"))
    graph.add_edge("C0", "D0", wind=wind("C0", "D0"))
    graph.add_edge("D0", "E0", wind=wind("D0", "E0"))
    # Horizontales fila 1
    graph.add_edge("A1", "B1", wind=wind("A1", "B1"))
    graph.add_edge("B1", "C1", wind=wind("B1", "C1"))
    graph.add_edge("C1", "D1", wind=wind("C1", "D1"))
    graph.add_edge("D1", "E1", wind=wind("D1", "E1"))
    # Horizontales fila 2
    graph.add_edge("A2", "B2", wind=wind("A2", "B2"))
    graph.add_edge("B2", "C2", wind=wind("B2", "C2"))
    graph.add_edge("C2", "D2", wind=wind("C2", "D2"))
    graph.add_edge("D2", "E2", wind=wind("D2", "E2"))
    # Horizontales fila 3
    graph.add_edge("A3", "B3", wind=wind("A3", "B3"))
    graph.add_edge("B3", "C3", wind=wind("B3", "C3"))
    graph.add_edge("C3", "D3", wind=wind("C3", "D3"))
    graph.add_edge("D3", "E3", wind=wind("D3", "E3"))

    # Verticales columna A (A2-A3 restringida, se omite)
    graph.add_edge("A0", "A1", wind=wind("A0", "A1"))
    graph.add_edge("A1", "A2", wind=wind("A1", "A2"))
    # Verticales columna B (B0-B1 restringida)
    graph.add_edge("B1", "B2", wind=wind("B1", "B2"))
    graph.add_edge("B2", "B3", wind=wind("B2", "B3"))
    # Verticales columna C (C1-C2 restringida)
    graph.add_edge("C0", "C1", wind=wind("C0", "C1"))
    graph.add_edge("C2", "C3", wind=wind("C2", "C3"))
    # Verticales columna D (D0-D1 restringida)
    graph.add_edge("D1", "D2", wind=wind("D1", "D2"))
    graph.add_edge("D2", "D3", wind=wind("D2", "D3"))
    # Verticales columna E (E2-E3 restringida)
    graph.add_edge("E0", "E1", wind=wind("E0", "E1"))
    graph.add_edge("E1", "E2", wind=wind("E1", "E2"))

    # Agregar atajos diagonales (sin bucles)
    graph.add_edge("A0", "B1", wind=0.9)
    graph.add_edge("B1", "C2", wind=1.3)
    graph.add_edge("C0", "D1", wind=1.6)
    graph.add_edge("C2", "D3", wind=1.0)
    graph.add_edge("A1", "B2", wind=0.6)

    start, goal = "A0", "E3"

    # Comparación BFS vs A*
    bfs_result = bfs(graph, start, goal, verbose=verbose)
    print("\n==== Resultados BFS ====")
    if bfs_result.path:
        print("Camino (BFS):", " -> ".join(bfs_result.path))
        print(f"Costo real (BFS): {bfs_result.cost:.3f} | Longitud (aristas): {len(bfs_result.path) - 1}")
    else:
        print("BFS: No hay camino disponible.")
    print(f"Nodos explorados (BFS): {bfs_result.explored}")
    print(f"Tiempo (BFS): {bfs_result.runtime_sec * 1000:.3f} ms \n\n")

    a_result = astar(graph, start, goal, verbose=verbose)
    print("\n==== Resultados A* ====")
    if a_result.path:
        print("Camino (A*):", " -> ".join(a_result.path))
        print(f"Costo total (A*): {a_result.cost:.3f}")
    else:
        print("A*: No hay camino disponible.")
    print(f"Nodos explorados (A*): {a_result.explored}")
    print(f"Tiempo (A*): {a_result.runtime_sec * 1000:.3f} ms")


if __name__ == "__main__":
    # Ejecuta la demo con trazas paso a paso
    demo(verbose=True)
