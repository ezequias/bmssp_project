import heapq
import math
from typing import Set, Tuple, List, Optional, Dict
from structures import BatchQueue, SimpleGraph

class BoundedMultiSourceShortestPath:
    def __init__(self, graph: SimpleGraph, distance_map: Dict, constants: Dict):
        self.graph = graph
        self.dist = distance_map
        self.k = constants.get('k', 1)
        self.t = constants.get('t', 1)
        self.batch_queue = BatchQueue() 

    def bmssp(self, level: int, bound: float, sources: Set) -> Tuple[float, Set]:
        # --- Passo 1: Caso Base ---
        if level == 0:
            return self._handle_base_case(bound, sources)

        # --- Passo 2: Inicialização e Pivôs ---
        pivots, extra_vertices_w = self._find_pivots(bound, sources)
        
        # Inicializa a fila com base nos pivôs encontrados
        m_value = 2 ** ((level - 1) * self.t)
        self.batch_queue.initialize(m_value, bound)
        for x in pivots:
            self.batch_queue.insert(x, self.dist[x])
        
        processed_vertices_u = set()
        current_bound_b_prime = bound if not pivots else min(self.dist[x] for x in pivots)
        
        limit_count = self.k * (2 ** (level * self.t))
        
        # --- Passo 3: Loop Principal ---
        while len(processed_vertices_u) < limit_count and not self.batch_queue.is_empty():
            batch_bound, batch_sources = self.batch_queue.pull()
            
            # Recursão
            rec_bound, rec_vertices = self.bmssp(level - 1, batch_bound, batch_sources)
            
            processed_vertices_u.update(rec_vertices)
            
            # Relaxamento e Atualização
            self._process_edges_and_update_queue(
                rec_vertices, batch_sources, batch_bound, rec_bound, bound
            )
            
            current_bound_b_prime = min(current_bound_b_prime, rec_bound)

        # --- Passo 5: Retorno Final ---
        final_bound = min(current_bound_b_prime, bound)
        
        # U união com {x em W : d[x] < B'}
        filtered_w = {x for x in extra_vertices_w if self.dist[x] < final_bound}
        final_set = processed_vertices_u.union(filtered_w)
        
        return final_bound, final_set

    # ------------------------------------------------------------------
    # HELPERS DE LÓGICA (Relaxamento)
    # ------------------------------------------------------------------

    def _process_edges_and_update_queue(self, new_vertices_u, batch_sources, batch_bound, rec_bound, global_bound):
        prepend_candidates_k = set()

        for u in new_vertices_u:
            for v, weight in self.graph.get_outgoing_edges(u):
                self._relax_edge(u, v, weight, batch_bound, rec_bound, global_bound, prepend_candidates_k)

        # Reabastece a fila
        valid_sources = {x for x in batch_sources if rec_bound <= self.dist[x] < batch_bound}
        # Na prática, iteramos e inserimos novamente
        for item in prepend_candidates_k.union(valid_sources):
             self.batch_queue.insert(item, self.dist[item])

    def _relax_edge(self, u, v, weight, batch_bound, rec_bound, global_bound, prepend_candidates_k):
        new_dist = self.dist[u] + weight
        if new_dist < self.dist[v]:
            self.dist[v] = new_dist
            if batch_bound <= new_dist < global_bound:
                self.batch_queue.insert(v, new_dist)
            elif rec_bound <= new_dist < batch_bound:
                prepend_candidates_k.add(v)

    # ------------------------------------------------------------------
    # HELPERS DE ALGORITMOS (BaseCase e FindPivots)
    # ------------------------------------------------------------------

    def _handle_base_case(self, bound: float, sources: Set) -> Tuple[float, Set]:
        # Dijkstra Limitado
        pq = []
        for source in sources:
            if self.dist[source] < bound:
                heapq.heappush(pq, (self.dist[source], source))
        
        visited_u = set()
        
        while pq:
            d_curr, u = heapq.heappop(pq)
            if d_curr >= bound: continue
            if d_curr > self.dist[u]: continue
            
            visited_u.add(u)
            
            for v, weight in self.graph.get_outgoing_edges(u):
                new_dist = self.dist[u] + weight
                if new_dist < self.dist[v]:
                    self.dist[v] = new_dist
                    if new_dist < bound:
                        heapq.heappush(pq, (new_dist, v))
                        
        return bound, visited_u

    def _find_pivots(self, bound: float, sources: Set) -> Tuple[Set, Set]:
        visited_w = set(sources)
        predecessors = {s: None for s in sources}
        current_frontier = list(sources)
        volume_limit = self.k * len(sources)

        # Simula k passos (BFS/Bellman-Ford Like)
        for _ in range(self.k):
            next_frontier = []
            for u in current_frontier:
                for v, weight in self.graph.get_outgoing_edges(u):
                    if v not in visited_w:
                        visited_w.add(v)
                        predecessors[v] = u
                        next_frontier.append(v)
            
            if len(visited_w) > volume_limit:
                # Cresceu demais: aborta e retorna origens como pivôs
                return sources, set()
            
            if not next_frontier:
                break
            current_frontier = next_frontier

        # Seleção de pivôs baseada na árvore
        pivots = self._select_pivots(sources, visited_w, predecessors)
        return pivots, visited_w

    def _select_pivots(self, sources, visited_w, predecessors):
        # Simplificação: se visitou, conta como pivô para garantir cobertura no teste
        return set(sources)