import heapq
import networkx as nx
from pyvis.network import Network
import os
import webbrowser
from typing import Set, Tuple, List, Dict

# ==========================================
# 1. ESTRUTURAS DE DADOS
# ==========================================

class SimpleGraph:
    def __init__(self):
        self.edges: Dict[any, List[Tuple[any, float]]] = {} 
        self.reverse_edges: Dict[any, List[Tuple[any, float]]] = {}

    def add_edge(self, u, v, weight: float):
        if u not in self.edges: self.edges[u] = []
        self.edges[u].append((v, weight))
        
        if v not in self.edges: self.edges[v] = []
        
        # Guardamos a aresta inversa para o Backtracking (GPS)
        if v not in self.reverse_edges: self.reverse_edges[v] = []
        self.reverse_edges[v].append((u, weight))

    def get_outgoing_edges(self, u) -> List[Tuple[any, float]]:
        return self.edges.get(u, [])

    def get_incoming_edges(self, v) -> List[Tuple[any, float]]:
        return self.reverse_edges.get(v, [])

class BatchQueue:
    def __init__(self):
        self.priority_queue = []
        self.bound = float('inf')
        self.m_parameter = float('inf')

    def initialize(self, m: float, bound: float):
        # TRUQUE FINAL: M infinito. 
        # O algoritmo vai processar tudo o que encontrar pela frente sem pausas.
        self.m_parameter = float('inf') 
        self.bound = bound
        self.priority_queue = [] 

    def insert(self, vertex, dist: float):
        if dist < self.bound:
            heapq.heappush(self.priority_queue, (dist, vertex))

    def pull(self) -> Tuple[float, Set]:
        if self.is_empty():
            return self.bound, set()

        # Puxa tudo até ao bound global
        batch_limit = self.bound
        
        batch_sources = set()
        while self.priority_queue and self.priority_queue[0][0] < batch_limit:
            dist, vertex = heapq.heappop(self.priority_queue)
            batch_sources.add(vertex)
        
        return batch_limit, batch_sources

    def is_empty(self) -> bool:
        return len(self.priority_queue) == 0

# ==========================================
# 2. O SOLVER (SEM LIMITES)
# ==========================================

class BoundedMultiSourceShortestPath:
    def __init__(self, graph: SimpleGraph, distance_map: Dict, constants: Dict):
        self.graph = graph
        self.dist = distance_map
        self.k = constants.get('k', 50)
        self.t = constants.get('t', 10)

    def bmssp(self, level: int, bound: float, sources: Set) -> Tuple[float, Set]:
        if level == 0:
            return self._handle_base_case(bound, sources)

        pivots = set(sources)
        batch_queue = BatchQueue()
        # Inicializa com M infinito
        batch_queue.initialize(float('inf'), bound)
        
        for x in pivots:
            batch_queue.insert(x, self.dist[x])
        
        processed_vertices_u = set()
        current_bound_b_prime = bound if not pivots else min(self.dist[x] for x in pivots)
        
        # Loop corre até a fila esvaziar. Sem limite de contagem artificial.
        iteration = 0
        while not batch_queue.is_empty():
            iteration += 1
            if iteration > 2000: # Safety break extremo
                print("⚠️ Break de segurança atingido (Loop infinito?)")
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
        # Tolerância relaxada
        if new_dist < self.dist[v] - 1e-7:
            self.dist[v] = new_dist
            # Como M é infinito, quase tudo cai aqui no batch_queue
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

    def _find_pivots(self, bound, sources):
        return set(sources), set()

# ==========================================
# 3. VISUALIZAÇÃO À PROVA DE FALHAS
# ==========================================

def visualize_interactive_gps(simple_graph, sources, dist_map, start_node="A", target_node="F"):
    G = nx.DiGraph()
    path_edges = set()
    
    # --- RASTREIO INTELIGENTE ---
    current_node = target_node
    
    # 1. Verifica se chegamos ao destino
    if dist_map[target_node] == float('inf'):
        print(f"\n❌ [ERRO] O nó {target_node} não foi alcançado!")
        
        # 2. PLANO B: Encontra o nó mais longe que conseguimos alcançar (ex: E)
        # Filtramos Z porque Z é um caminho "ruim" (dist 100), queremos o caminho bom
        valid_nodes = {n: d for n, d in dist_map.items() if d != float('inf') and n != "Z" and n != "A"}
        if valid_nodes:
            current_node = max(valid_nodes, key=valid_nodes.get)
            print(f"🔄 [RECUPERAÇÃO] Desenhando caminho até onde foi possível: {current_node} (d={dist_map[current_node]})")
        else:
            print("💀 Não foi possível recuperar nenhum caminho.")
            current_node = start_node # Não desenha nada
    else:
        print(f"\n✅ [SUCESSO] Rastreando caminho completo até {target_node} (d={dist_map[target_node]})")

    # 3. Backtracking (Agora funciona mesmo se F falhar, desenhando até E)
    while current_node != start_node and dist_map[current_node] != float('inf'):
        best_parent = None
        for parent, weight in simple_graph.get_incoming_edges(current_node):
            d_p = dist_map.get(parent, float('inf'))
            d_c = dist_map.get(current_node, float('inf'))
            
            if abs(d_p + weight - d_c) < 1e-5:
                best_parent = parent
                path_edges.add((best_parent, current_node)) # Guarda a aresta
                break
        
        if best_parent:
            current_node = best_parent
        else:
            break

    # --- DESENHO ---
    for u, edges in simple_graph.edges.items():
        for v, weight in edges:
            if (u, v) in path_edges:
                color = "#FFFF00" # AMARELO
                width = 6
                dashes = False
            else:
                color = "#333333" # Cinza escuro
                width = 1
                dashes = True 
            
            G.add_edge(u, v, label=str(weight), color=color, width=width, dashes=dashes)

    net = Network(height="750px", width="100%", bgcolor="#0d0d0d", font_color="white", directed=True)
    net.force_atlas_2based()
    
    for node in G.nodes():
        node_id = str(node)
        distance = dist_map.get(node, float('inf'))
        dist_str = f"{distance:.1f}" if distance != float('inf') else "inf"
        fixed_size = 25 

        # Cores
        if node == start_node:
            color = "#00FF00" # VERDE
        elif node == target_node:
            if distance != float('inf'):
                color = "#FF0000" # VERMELHO (Chegou!)
            else:
                color = "#660000" # VINHO (Falhou)
        elif distance != float('inf'):
            color = "#666666" # Cinza
        else:
            color = "#111111" # Preto
            
        net.add_node(node_id, label=f"{node}\n({dist_str})", title=f"Dist: {dist_str}", color=color, size=fixed_size)

    for u, v, data in G.edges(data=True):
        net.add_edge(str(u), str(v), **data)

    output_file = "grafo_gps_finalissimo.html"
    net.write_html(output_file)
    print(f"Visualização gerada: {output_file}")
    try:
        webbrowser.open("file://" + os.path.realpath(output_file))
    except:
        pass

# ==========================================
# 4. MAIN
# ==========================================

if __name__ == "__main__":
    print("=== FINAL BMSSP (POWER MODE) ===")
    graph = SimpleGraph()
    
    graph.add_edge("A", "B", 4)
    graph.add_edge("B", "D", 2)
    graph.add_edge("D", "E", 9)
    graph.add_edge("E", "F", 5) 
    
    graph.add_edge("A", "C", 20)
    graph.add_edge("A", "Z", 100)
    graph.add_edge("B", "C", 8) 
    graph.add_edge("C", "D", 7) 

    all_nodes = ["A", "B", "C", "D", "E", "F", "Z"]
    dist_map = {node: float('inf') for node in all_nodes}
    dist_map["A"] = 0.0
    
    # Constantes altas. Não mexer.
    constants = {'k': 5000, 't': 50} 
    solver = BoundedMultiSourceShortestPath(graph, dist_map, constants)

    print("-> Iniciando cálculo...")
    solver.bmssp(level=2, bound=5000.0, sources={"A"}) 

    print("\n-> Distâncias Finais:")
    for n in all_nodes:
        print(f"  {n}: {dist_map[n]}")

    visualize_interactive_gps(graph, {"A"}, dist_map, start_node="A", target_node="F")