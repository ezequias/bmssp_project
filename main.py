import networkx as nx
from pyvis.network import Network
import os
import webbrowser
from structures import SimpleGraph
from solver import BoundedMultiSourceShortestPath

# ==========================================
# VISUALIZAÇÃO GPS (ROBUSTA)
# ==========================================
def visualize_interactive_gps(simple_graph, sources, dist_map, start_node="A", target_node="F"):
    G = nx.DiGraph()
    path_edges = set()
    
    # --- RASTREIO INTELIGENTE ---
    current_node = target_node
    
    # 1. Verifica se chegamos ao destino
    if dist_map[target_node] == float('inf'):
        print(f"\n❌ [VISUALIZADOR] O nó {target_node} não foi alcançado!")
        # Fallback: Encontra o nó alcançável mais distante (excluindo Z e caminhos ruins)
        valid_nodes = {n: d for n, d in dist_map.items() if d != float('inf') and n != "Z" and d < 500}
        if valid_nodes:
            current_node = max(valid_nodes, key=valid_nodes.get)
            print(f"🔄 [RECUPERAÇÃO] Desenhando caminho até: {current_node}")
        else:
            current_node = start_node
    else:
        print(f"\n✅ [VISUALIZADOR] Rota encontrada até {target_node} (Custo: {dist_map[target_node]})")

    # 2. Backtracking (GPS)
    while current_node != start_node and dist_map[current_node] != float('inf'):
        best_parent = None
        # Procura nos pais quem satisfaz: Dist(Pai) + Peso = Dist(Filho)
        for parent, weight in simple_graph.get_incoming_edges(current_node):
            d_p = dist_map.get(parent, float('inf'))
            d_c = dist_map.get(current_node, float('inf'))
            
            if abs(d_p + weight - d_c) < 1e-5:
                best_parent = parent
                path_edges.add((best_parent, current_node))
                break
        
        if best_parent:
            current_node = best_parent
        else:
            break

    # --- DESENHO DO GRAFO ---
    # Adiciona nós e arestas ao NetworkX para exportar para PyVis
    for u, edges in simple_graph.edges.items():
        for v, weight in edges:
            if (u, v) in path_edges:
                color = "#FFFF00" # AMARELO (Rota GPS)
                width = 6
                dashes = False
            else:
                color = "#333333" # Cinza Escuro (Fundo)
                width = 1
                dashes = True 
            
            G.add_edge(u, v, label=str(weight), color=color, width=width, dashes=dashes)

    # Configuração PyVis
    net = Network(height="450px", width="100%", bgcolor="#0d0d0d", font_color="white", directed=True)
    net.force_atlas_2based()
    net.show_buttons(filter_=['physics'])
    
    for node in G.nodes():
        node_id = str(node)
        distance = dist_map.get(node, float('inf'))
        dist_str = f"{distance:.1f}" if distance != float('inf') else "inf"
        fixed_size = 25 

        # Cores dos Nós
        if node == start_node:
            color = "#00FF00" # VERDE (Início)
        elif node == target_node:
            if distance != float('inf'):
                color = "#FF0000" # VERMELHO (Chegou!)
            else:
                color = "#660000" # VINHO (Não chegou)
        elif distance != float('inf'):
            color = "#666666" # Cinza (Visitado)
        else:
            color = "#111111" # Preto (Não visitado)
            
        net.add_node(node_id, label=f"{node}\n({dist_str})", title=f"Dist: {dist_str}", color=color, size=fixed_size)

    for u, v, data in G.edges(data=True):
        net.add_edge(str(u), str(v), **data)

    output_file = "grafo_bmssp_final.html"
    net.write_html(output_file)
    print(f"Visualização gerada: {output_file}")
    try:
        webbrowser.open("file://" + os.path.realpath(output_file))
    except:
        pass

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
def main():
    print("=== FINAL BMSSP (ESTRUTURA MODULAR) ===")
    graph = SimpleGraph()
    
    # --- Definição do Grafo ---
    # Caminho ideal
    graph.add_edge("A", "B", 4)
    graph.add_edge("B", "D", 2)
    graph.add_edge("D", "E", 9)
    graph.add_edge("E", "F", 5) 
    
    # Caminhos alternativos/ruins
    graph.add_edge("A", "C", 20)
    graph.add_edge("A", "Z", 100)
    graph.add_edge("B", "C", 8) 
    graph.add_edge("C", "D", 7) 

    all_nodes = ["A", "B", "C", "D", "E", "F", "Z"]
    dist_map = {node: float('inf') for node in all_nodes}
    dist_map["A"] = 0.0
    
    # --- Configuração do Solver ---
    # Parâmetros "Power Mode" para garantir execução total
    constants = {'k': 5000, 't': 50} 
    solver = BoundedMultiSourceShortestPath(graph, dist_map, constants)

    print("-> Iniciando cálculo...")
    solver.bmssp(level=2, bound=5000.0, sources={"A"}) 

    print("\n-> Resultados:")
    for n in all_nodes:
        print(f"  {n}: {dist_map[n]}")

    # --- Visualização ---
    visualize_interactive_gps(graph, {"A"}, dist_map, start_node="A", target_node="F")

if __name__ == "__main__":
    main()