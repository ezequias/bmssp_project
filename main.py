import json
import networkx as nx
from pyvis.network import Network
import os
import webbrowser
from structures import SimpleGraph
from solver import BoundedMultiSourceShortestPath

import json

import json

def visualize_interactive_gps(simple_graph, sources, dist_map, start_node="A", target_node="F"):
    # --- RASTREIO DO CAMINHO (Mantido) ---
    path_edges = set()
    current_node = target_node
    if dist_map.get(target_node, float('inf')) != float('inf'):
        while current_node != start_node:
            found = False
            for parent, weight in simple_graph.get_incoming_edges(current_node):
                if abs(dist_map.get(parent, float('inf')) + weight - dist_map[current_node]) < 1e-5:
                    path_edges.add((parent, current_node))
                    current_node = parent
                    found = True
                    break
            if not found: break

    # --- CONFIGURAÇÃO DA REDE ---
    # Removido o 'heading' daqui para evitar duplicidade
    net = Network(height="600px", width="100%", bgcolor="#0d0d0d", font_color="white", directed=True)
    
    # Adicionar Nós
    for node_id in dist_map.keys():
        dist = dist_map[node_id]
        label = f"{node_id}\n({dist:.1f})"
        if node_id == start_node: color = "#00FF00"
        elif node_id == target_node: color = "#FF0000" if dist != float('inf') else "#660000"
        else: color = "#444444"
        net.add_node(str(node_id), label=label, color=color, size=25)

    # Adicionar Arestas
    for u, edges in simple_graph.edges.items():
        for v, weight in edges:
            is_gps = (u, v) in path_edges
            net.add_edge(str(u), str(v), label=str(weight), 
                         color="#FFFF00" if is_gps else "#333333", 
                         width=5 if is_gps else 1, arrows="to")

    net.force_atlas_2based(spring_length=250)
    net.show_buttons(filter_=['physics'])

    # --- CUSTOMIZAÇÃO DO TÍTULO E CORES ---
    html_content = net.generate_html()
    
    # Criamos um cabeçalho personalizado com cores específicas
    custom_header = f"""
    <div style="background-color: #0d0d0d; color: white; padding: 20px; text-align: center; font-family: sans-serif; border-bottom: 1px solid #333;">
        <h2 style="margin: 0; font-size: 24px;">
            Melhor Caminho SSSP DE: 
            <span style="color: #00FF00;">{start_node}</span> 
            Para: 
            <span style="color: #FF0000;">{target_node}</span>
        </h2>
    </div>
    """
    
    # Injetamos o cabeçalho logo após a abertura do <body>
    html_content = html_content.replace("<body>", f"<body>{custom_header}")

    # Salvar e Abrir
    output_file = "grafo_final_estilizado.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ Sucesso! Título estilizado gerado em: {output_file}")
    webbrowser.open("file://" + os.path.realpath(output_file))
    
def load_graph_data(filename, graph_obj):
    """Carrega nós e arestas de um JSON e popula o grafo."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for edge in data['edges']:
                graph_obj.add_edge(edge['u'], edge['v'], edge['w'])
            return data['nodes']
    except FileNotFoundError:
        print(f"❌ Erro: O ficheiro {filename} não foi encontrado!")
        return None

def main():
    print("=== FINAL BMSSP (CARREGANDO CENÁRIO 30 ARESTAS) ===")
    graph = SimpleGraph()
    
    # --- ESCOLHA DO CENÁRIO ---
    cenario_arquivo = "cenario_complexo.json"  # Altere conforme necessário

    all_nodes = load_graph_data(cenario_arquivo, graph)
    
    if not all_nodes:
        return # Interrompe se o ficheiro não for lido

    # Inicializa distâncias
    dist_map = {node: float('inf') for node in all_nodes}
    dist_map["A"] = 0.0 # Ponto de partida
    
    # Solver
    constants = {'k': 5000, 't': 50} 
    solver = BoundedMultiSourceShortestPath(graph, dist_map, constants)
    solver.bmssp(level=2, bound=5000.0, sources={"A"}) 

    # Visualização (Alvo: "F" ou "O" conforme o JSON)
    visualize_interactive_gps(graph, {"A"}, dist_map, start_node="A", target_node="F")

if __name__ == "__main__":
    main()