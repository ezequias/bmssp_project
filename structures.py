import heapq
from typing import List, Tuple, Dict, Set, Any

class SimpleGraph:
    def __init__(self):
        self.edges: Dict[Any, List[Tuple[Any, float]]] = {} 
        # Adicionado para suportar o Backtracking (GPS)
        self.reverse_edges: Dict[Any, List[Tuple[Any, float]]] = {}

    def add_edge(self, u, v, weight: float):
        # Aresta normal (Ida)
        if u not in self.edges: self.edges[u] = []
        self.edges[u].append((v, weight))
        
        # Garante que o nó de destino existe no dicionário
        if v not in self.edges: self.edges[v] = []
        
        # Aresta inversa (Volta) - Vital para o visualizador GPS
        if v not in self.reverse_edges: self.reverse_edges[v] = []
        self.reverse_edges[v].append((u, weight))

    def get_outgoing_edges(self, u) -> List[Tuple[Any, float]]:
        return self.edges.get(u, [])

    def get_incoming_edges(self, v) -> List[Tuple[Any, float]]:
        return self.reverse_edges.get(v, [])

class BatchQueue:
    def __init__(self):
        self.priority_queue = []
        self.bound = float('inf')
        self.m_parameter = float('inf')

    def initialize(self, m: float, bound: float):
        # MODO POWER: Ignoramos o 'm' calculado e usamos o bound total.
        # Isto garante robustez máxima em grafos complexos ou pequenos.
        self.m_parameter = bound 
        self.bound = bound
        self.priority_queue = [] 

    def insert(self, vertex, dist: float):
        if dist < self.bound:
            heapq.heappush(self.priority_queue, (dist, vertex))

    def pull(self) -> Tuple[float, Set]:
        if self.is_empty():
            return self.bound, set()

        # Puxa tudo até ao limite global (comportamento atómico)
        batch_limit = self.bound
        
        batch_sources = set()
        while self.priority_queue and self.priority_queue[0][0] < batch_limit:
            dist, vertex = heapq.heappop(self.priority_queue)
            batch_sources.add(vertex)
        
        return batch_limit, batch_sources

    def is_empty(self) -> bool:
        return len(self.priority_queue) == 0