import heapq
from typing import Set, Tuple, List, Iterable, Dict

class SimpleGraph:
    """
    Uma implementação simples de Grafo Direcionado usando lista de adjacências.
    """
    def __init__(self):
        self.edges: Dict[any, List[Tuple[any, float]]] = {} 

    def add_edge(self, u, v, weight: float):
        if u not in self.edges: 
            self.edges[u] = []
        self.edges[u].append((v, weight))
        # Garante que o destino também existe no dicionário para evitar erros de chave
        if v not in self.edges:
            self.edges[v] = []

    def get_outgoing_edges(self, u) -> List[Tuple[any, float]]:
        return self.edges.get(u, [])

class BatchQueue:
    """
    Implementação da estrutura D baseada em Min-Heap para simular
    o processamento em lotes do algoritmo.
    """
    def __init__(self):
        self.priority_queue = []
        self.bound = float('inf')
        self.m_parameter = 1

    def initialize(self, m: int, bound: float):
        self.m_parameter = m
        self.bound = bound
        self.priority_queue = [] 

    def insert(self, vertex, dist: float):
        if dist < self.bound:
            heapq.heappush(self.priority_queue, (dist, vertex))

    def batch_prepend(self, items: Iterable[any]):
        """Adiciona itens à fila (pode receber um set ou lista de vértices/tuplos)."""
        # Nota: Na implementação real, items pode ser só vértices ou (v, dist).
        # Aqui assumimos que quem chama já tratou das distâncias ou passamos explicitamente.
        pass 
        # ATENÇÃO: Para simplificar a integração com o código principal que usa 
        # insert individualmente, este método é um placeholder para a lógica complexa
        # de "Prepend" do paper. A lógica de insert principal acontece no loop.

    def pull(self) -> Tuple[float, Set]:
        if self.is_empty():
            return self.bound, set()

        current_min_dist = self.priority_queue[0][0]
        batch_sources = set()

        while self.priority_queue and self.priority_queue[0][0] == current_min_dist:
            dist, vertex = heapq.heappop(self.priority_queue)
            batch_sources.add(vertex)

        return current_min_dist, batch_sources

    def is_empty(self) -> bool:
        return len(self.priority_queue) == 0