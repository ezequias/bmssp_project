import unittest
import json
import os
import sys

# Garante que o projeto seja encontrado
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.structures import SimpleGraph
from src.solver import BoundedMultiSourceShortestPath
from main import visualize_interactive_gps

class TestBMSSPAutomated(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(BASE_DIR, 'data')

    def run_scenario_logic(self, json_file):
        """Este é o molde que processa qualquer JSON."""
        path = os.path.join(self.data_dir, json_file)
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Criação do grafo (A variável 'graph' nasce aqui)
        graph = SimpleGraph()
        for e in data['edges']:
            graph.add_edge(e['u'], e['v'], e['w'])
            
        tp = data['test_params']
        dist_map = {node: float('inf') for node in data['nodes']}
        dist_map[tp['start_node']] = 0.0
        
        solver = BoundedMultiSourceShortestPath(graph, dist_map, tp['constants'])
        solver.bmssp(level=tp['level'], bound=tp['bound'], sources={tp['start_node']})
        
        # Validação
        self.assertAlmostEqual(dist_map[tp['target_node']], tp['expected_cost'], places=4)

        # Geração do HTML individual
        output_name = f"resultado_{json_file.replace('.json', '.html')}"
        visualize_interactive_gps(
            graph, 
            dist_map, 
            tp['start_node'], 
            tp['target_node'], 
            filename=output_name
        )

    def test_cenario_simples(self):
        """Gatilho para o teste simples."""
        self.run_scenario_logic('cenario_simples.json')

    def test_cenario_complexo(self):
        """Gatilho para o teste complexo."""
        self.run_scenario_logic('cenario_complexo.json')

if __name__ == "__main__":
    unittest.main()