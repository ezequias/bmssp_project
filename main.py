from structures import SimpleGraph
from solver import BoundedMultiSourceShortestPath

def main():
    print("=== Iniciando BMSSP Demo ===")

    # 1. Configurar o Grafo
    graph = SimpleGraph()
    # Criando um grafo interessante: A -> B -> C -> D
    # Com um atalho de A -> C (mais longo) e A -> D (muito longo)
    graph.add_edge("A", "B", 10)
    graph.add_edge("B", "C", 10)
    graph.add_edge("C", "D", 10)
    
    # Caminho alternativo mais curto para C? Não, mais longo (30)
    graph.add_edge("A", "C", 30)
    
    # E um ciclo para testar robustez: D -> B
    graph.add_edge("D", "B", 5)

    # 2. Configurar Estado Inicial
    # Vamos calcular distâncias a partir de "A"
    all_nodes = ["A", "B", "C", "D"]
    dist_map = {node: float('inf') for node in all_nodes}
    dist_map["A"] = 0.0

    constants = {'k': 2, 't': 1} # k=2 (passos de exploração), t=1 (fator de escala)

    # 3. Instanciar o Solver
    solver = BoundedMultiSourceShortestPath(graph, dist_map, constants)

    # 4. Executar o Algoritmo
    # Level 2 de recursão, Limite (Bound) de 100
    print("A executar bmssp(level=2, bound=100)...")
    final_bound, visited_set = solver.bmssp(level=2, bound=100.0, sources={"A"})

    # 5. Resultados
    print("\n=== Resultados Finais ===")
    print(f"Vértices Visitados: {visited_set}")
    print("\nDistâncias Calculadas:")
    for node, d in dist_map.items():
        print(f"  {node}: {d}")

    # Validação Básica
    print("\nVerificação:")
    print(f"- Distância B esperada: 10.0 -> Obtida: {dist_map['B']}")
    print(f"- Distância C esperada: 20.0 (A->B->C) -> Obtida: {dist_map['C']}")
    print(f"- Distância D esperada: 30.0 (A->B->C->D) -> Obtida: {dist_map['D']}")

if __name__ == "__main__":
    main()