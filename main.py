import os    # <--- IMPORTANTE: Deve ser o primeiro
import sys   # <--- IMPORTANTE: Deve ser o segundo
import json
import webbrowser
from pyvis.network import Network

# Adiciona a raiz do projeto ao PATH para que o Python encontre a pasta 'src'
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Imports do seu código fonte
from src.structures import SimpleGraph
from src.solver import BoundedMultiSourceShortestPath

def print_path_summary(dist_map, start_node, target_node, graph):
    """Extrai e imprime a rota e o custo total no console."""
    path = []
    curr = target_node
    total_cost = dist_map.get(target_node, float('inf'))

    if total_cost == float('inf'):
        print(f"\n❌ ROTA NÃO ENCONTRADA: Não há caminho de {start_node} para {target_node}")
        return

    # Backtracking para reconstruir a lista de nós
    while curr != start_node:
        path.append(curr)
        found = False
        for p, w in graph.get_incoming_edges(curr):
            if abs(dist_map.get(p, float('inf')) + w - dist_map[curr]) < 1e-5:
                curr = p
                found = True
                break
        if not found: break
    
    path.append(start_node)
    path.reverse() # Inverte para ficar de Start -> Target

    # Imprime no console com setas
    print("\n" + "="*50)
    print(f"📍 RESUMO DA ROTA (GPS)")
    print(f"🟩 Origem: {start_node} | 🏁 Destino: {target_node}")
    print(f"🛣️  Caminho: {' ➔ '.join(path)}")
    print(f"💰 Custo Total: {total_cost:.2f}")
    print("="*50 + "\n")

def visualize_interactive_gps(graph, dist_map, start_node, target_node, filename="resultado_gps.html"):
    # 1. Backtracking (Lógica da rota amarela)
    path_edges = set()
    curr = target_node
    if dist_map.get(curr, float('inf')) != float('inf'):
        while curr != start_node:
            found = False
            for p, w in graph.get_incoming_edges(curr):
                if abs(dist_map.get(p, float('inf')) + w - dist_map[curr]) < 1e-5:
                    path_edges.add((p, curr))
                    curr = p
                    found = True
                    break
            if not found: break

    # 2. CRIAR O OBJETO 'net' (ESTA LINHA DEVE VIR ANTES DE QUALQUER 'net.')
    net = Network(height="700px", width="100%", bgcolor="#0d0d0d", font_color="white", directed=True)
    
    # 3. Adicionar Nós e Arestas
    for n, d in dist_map.items():
        color = "#00FF00" if n == start_node else ("#FF0000" if n == target_node else "#444444")
        net.add_node(n, label=f"{n}\n({d:.1f})", color=color, size=25)

    for u, edges in graph.edges.items():
        for v, w in edges:
            is_gps = (u, v) in path_edges
            net.add_edge(u, v, label=str(w), 
                         color="#FFFF00" if is_gps else "#333333", 
                         width=5 if is_gps else 1, arrows="to")

    net.force_atlas_2based(spring_length=250)
    
    # 4. AGORA SIM, GERAR O HTML (net já existe aqui)
    html_content = net.generate_html()
    
    # Injeção do título e gravação na pasta 'output'
    output_dir = "output"
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    
    filepath = os.path.join(output_dir, filename)
    
    custom_header = f'<div style="background:#1a1a1a; color:white; padding:15px; text-align:center;"><h2 style="margin:0;">SSSP: <span style="color:#00FF00">{start_node}</span> para <span style="color:#FF0000">{target_node}</span></h2></div>'
    html_content = html_content.replace("<body>", f"<body>{custom_header}")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    webbrowser.open("file://" + os.path.abspath(filepath))

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
    print("=== FINAL BMSSP (EXECUTANDO CENÁRIO COMPLEXO) ===")
    graph = SimpleGraph()
    
    # 1. Carregar Dados do SEU ficheiro
    cenario_arquivo = os.path.join("data", "cenario_complexo.json")
    all_nodes = load_graph_data(cenario_arquivo, graph)
    
    if not all_nodes:
        return 

    # 2. Configuração Inicial das Distâncias
    # Para o algoritmo funcionar como SSSP, a origem deve ser 0.0
    dist_map = {node: float('inf') for node in all_nodes}
    dist_map["A"] = 0.0 
    
    # 3. Executar o Solver (Onde a magia acontece)
    constants = {'k': 5000, 't': 50} 
    solver = BoundedMultiSourceShortestPath(graph, dist_map, constants)
    
    # O solver vai preencher o dist_map com os valores corretos
    solver.bmssp(level=2, bound=5000.0, sources={"A"}) 

    # 🆕 NOVO: Mostrar no console
    print_path_summary(dist_map, "A", "F", graph)

    # 4. Visualização Final (CHAMADA ÚNICA)
    # Removido o argumento extra {"A"} para evitar o TypeError
    visualize_interactive_gps(graph, dist_map, start_node="A", target_node="F")

if __name__ == "__main__":
    main()