import heapq
from typing import Set, Tuple, Dict
from .structures import SimpleGraph, BatchQueue

class BoundedMultiSourceShortestPath:
    def __init__(self, graph: SimpleGraph, distance_map: Dict, constants: Dict):
        self.graph = graph
        self.dist = distance_map
        self.k = constants.get('k', 5000)
        self.t = constants.get('t', 50)

    def bmssp(self, level: int, bound: float, sources: Set) -> Tuple[float, Set]:
        # --- Passo 1: Caso Base ---
        if level == 0:
            return self._handle_base_case(bound, sources)

        # --- Passo 2: Inicialização ---
        pivots = set(sources)
        batch_queue = BatchQueue()
        # Inicializa com bound total (lógica definida no BatchQueue)
        batch_queue.initialize(bound, bound)
        
        for x in pivots:
            batch_queue.insert(x, self.dist[x])
        
        processed_vertices_u = set()
        current_bound_b_prime = bound if not pivots else min(self.dist[x] for x in pivots)
        
        # --- Passo 3: Loop Principal ---
        iteration = 0
        while not batch_queue.is_empty():
            iteration += 1
            # Travão de segurança para grafos pequenos: 500 é mais que suficiente
            if iteration > 500: 
                break 

            batch_bound, batch_sources = batch_queue.pull()
            if not batch_sources: break

            rec_bound, rec_vertices = self.bmssp(level - 1, batch_bound, batch_sources)
            processed_vertices_u.update(rec_vertices)
            
            self._process_edges_and_update_queue(
                rec_vertices, batch_sources, batch_bound, rec_bound, bound, batch_queue
            )
            current_bound_b_prime = min(current_bound_b_prime, rec_bound)

        return min(current_bound_b_prime, bound), processed_vertices_u

    def _process_edges_and_update_queue(self, new_vertices_u, batch_sources, batch_bound, rec_bound, global_bound, batch_queue):
        prepend_candidates_k = set()
        for u in new_vertices_u:
            for v, weight in self.graph.get_outgoing_edges(u):
                self._relax_edge(u, v, weight, batch_bound, rec_bound, global_bound, prepend_candidates_k, batch_queue)

        if rec_bound < batch_bound:
            valid_sources = {x for x in batch_sources if rec_bound <= self.dist[x] < batch_bound}
            for item in prepend_candidates_k.union(valid_sources):
                batch_queue.insert(item, self.dist[item])

    def _relax_edge(self, u, v, weight, batch_bound, rec_bound, global_bound, prepend_candidates_k, batch_queue):
        new_dist = self.dist[u] + weight
        # Tolerância relaxada para garantir update (corrige problemas de precisão float)
        if new_dist < self.dist[v] - 1e-7:
            self.dist[v] = new_dist
            if batch_bound <= new_dist < global_bound:
                batch_queue.insert(v, new_dist)
            elif rec_bound <= new_dist < batch_bound:
                prepend_candidates_k.add(v)

    def _handle_base_case(self, bound: float, sources: Set) -> Tuple[float, Set]:
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