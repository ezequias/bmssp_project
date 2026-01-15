import networkx as nx
# Removemos o matplotlib
from pyvis.network import Network
import os
import webbrowser

from structures import SimpleGraph
from solver import BoundedMultiSourceShortestPath

def visualize_interactive(simple_graph, sources, visited_set, dist_map):
    """
    Gera um grafo onde o MELHOR CAMINHO é destacado a AMARELO.
    """
    G = nx.DiGraph()
    
    # Adicionar arestas com lógica de coloração
    for u, edges in simple_graph.edges.items():
        for v, weight in edges:
            dist_u = dist_map.get(u, float('inf'))
            dist_v = dist_map.get(v, float('inf'))
            
            is_best_path = False
            # Só pintamos se ambos os nós tiverem sido alcançados (não infinito)
            if dist_u != float('inf') and dist_v != float('inf'):
                # Verifica matemática: Distância Origem->U + Peso == Distância Origem->V
                if abs(dist_u + weight - dist_v) < 1e-9:
                    is_best_path = True

            if is_best_path:
                color = "#FFFF00" # <--- AMARELO (Yellow)
                width = 4         # Mais grosso para destaque
                style = "solid"
                highlight = True
            else:
                color = "#555555" # Cinzento escuro para contraste no fundo preto
                width = 1
                style = "dashed"
                highlight = False

            G.add_edge(u, v, label=str(weight), weight=weight, color=color, width=width, dashes=not is_best_path)

    # Configuração da Rede (Fundo escuro para o amarelo brilhar)
    net = Network(height="750px", width="100%", bgcolor="#111111", font_color="white", directed=True)
    net.force_atlas_2based()

    # Adicionar Nós
    for node in G.nodes():
        node_id = str(node)
        distance = dist_map.get(node, float('inf'))
        dist_str = f"{distance:.1f}" if distance != float('inf') else "inf"
        
        if node in sources:
            color = "#ff4444" # Vermelho/Laranja para Origem
            size = 25
        elif node in visited_set:
            color = "#75a478" # Verde suave para Visitados
            size = 20
        else:
            color = "#444444" # Cinzento para inalcançáveis
            size = 15

        label_display = f"{node}\n(d={dist_str})"
        net.add_node(node_id, label=label_display, title=f"Dist: {dist_str}", color=color, size=size)

    # Adicionar Arestas
    for u, v, data in G.edges(data=True):
        net.add_edge(str(u), str(v), label=data['label'], color=data['color'], width=data['width'], dashes=data['dashes'])

    # Salvar e Abrir
    output_file = "grafo_amarelo.html"
    net.write_html(output_file)
    print(f"Visualização gerada: {output_file}")
    
    try:
        file_path = "file://" + os.path.realpath(output_file)
        webbrowser.open(file_path)
    except:
        print(f"Abra manualmente o ficheiro {output_file}")
        
def main():
    print("=== Iniciando BMSSP Interativo ===")

    # 1. Configurar o Grafo
    graph = SimpleGraph()
    
    # Mesmo grafo do exemplo anterior
    graph.add_edge("A", "B", 4)
    graph.add_edge("B", "C", 8)
    graph.add_edge("C", "D", 7)
    graph.add_edge("D", "E", 9)
    graph.add_edge("A", "C", 20)     
    graph.add_edge("B", "D", 2)      
    graph.add_edge("E", "F", 5)
    graph.add_edge("A", "Z", 100)    

    # 2. Setup
    all_nodes = ["A", "B", "C", "D", "E", "F", "Z"]
    dist_map = {node: float('inf') for node in all_nodes}
    dist_map["A"] = 0.0
    sources = {"A"}

    # 3. Executar Solver
    constants = {'k': 2, 't': 1} 
    solver = BoundedMultiSourceShortestPath(graph, dist_map, constants)

    print("A calcular caminhos...")
    final_bound, visited_set = solver.bmssp(level=3, bound=25.0, sources=sources)

    print(f"Bound Final: {final_bound}")
    print(f"Visitados: {visited_set}")

    # 4. Visualizar Interativamente
    print("A gerar visualização interativa...")
    visualize_interactive(graph, sources, visited_set, dist_map)

if __name__ == "__main__":
    main()