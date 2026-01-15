import heapq
from typing import Set, Tuple, List, Dict, Iterable

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
        if v not in self.edges:
            self.edges[v] = []

    def get_outgoing_edges(self, u) -> List[Tuple[any, float]]:
        return self.edges.get(u, [])

class BatchQueue:
    """
    Implementação da estrutura D corrigida para processar intervalos (Buckets).
    """
    def __init__(self):
        self.priority_queue = []
        self.bound = float('inf')
        self.m_parameter = 1.0 # M: O tamanho do passo/bucket

    def initialize(self, m: float, bound: float):
        self.m_parameter = max(m, 1.0) # Garante que o passo é pelo menos 1
        self.bound = bound
        self.priority_queue = [] 

    def insert(self, vertex, dist: float):
        if dist < self.bound:
            heapq.heappush(self.priority_queue, (dist, vertex))

    def pull(self) -> Tuple[float, Set]:
        """
        Retira um lote de vértices.
        Em vez de retirar apenas o mínimo exato, retira tudo dentro do intervalo [min, min + M).
        """
        if self.is_empty():
            return self.bound, set()

        # 1. Determinar o intervalo do lote
        current_min_dist = self.priority_queue[0][0]
        
        # O limite deste lote é o mínimo + o parâmetro M (o tamanho do passo)
        # Ex: Se min=0 e M=4, processamos tudo até 4.
        batch_limit = current_min_dist + self.m_parameter
        
        # Não podemos ultrapassar o limite global B
        batch_limit = min(batch_limit, self.bound)

        batch_sources = set()

        # 2. Retirar tudo o que cabe neste intervalo
        # Nota: Retiramos elementos estritamente menores que o limite do lote
        # para dar espaço à recursão processar até esse limite.
        while self.priority_queue and self.priority_queue[0][0] < batch_limit:
            dist, vertex = heapq.heappop(self.priority_queue)
            batch_sources.add(vertex)
            
        # Se por acaso o bucket ficar vazio (ex: distancias iguais ao limit),
        # forçamos a retirada de pelo menos o mínimo para evitar loops infinitos
        if not batch_sources and self.priority_queue:
             dist, vertex = heapq.heappop(self.priority_queue)
             batch_sources.add(vertex)
             batch_limit = max(batch_limit, dist + 0.0001)

        return batch_limit, batch_sources

    def is_empty(self) -> bool:
        return len(self.priority_queue) == 0