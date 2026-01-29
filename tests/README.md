# 🧪 Suíte de Testes Automatizados - BMSSP

Este diretório contém os scripts de testes automatizados para o algoritmo **Bounded Multi-Source Shortest Path (BMSSP)**. O objetivo é garantir a precisão dos cálculos de caminho mínimo e gerar visualizações interativas automaticamente.

---

## 📌 Visão Geral

O script `test_bmssp.py` utiliza o framework `unittest` para realizar testes baseados em dados (Data-Driven Testing). Ele separa a lógica do teste (Python) da definição dos dados (JSON), permitindo que novos cenários de malhas viárias ou grafos sejam testados sem alterar o código principal.

### Estrutura de Arquivos Relacionados
* `src/structures.py`: Contém a classe `SimpleGraph`.
* `src/solver.py`: Contém a implementação do algoritmo `BoundedMultiSourceShortestPath`.
* `main.py`: Contém a função de visualização `visualize_interactive_gps`.
* `data/*.json`: Arquivos de configuração de cenários.

---

## 🛠️ O Motor de Teste: `run_scenario_logic`

A função principal da suíte é o "molde" `run_scenario_logic`. Ela executa as seguintes etapas para cada arquivo JSON:

1. **Instanciação do Grafo**: Lê as arestas do JSON e popula o `SimpleGraph`.
2. **Setup do Solver**: Inicializa o mapa de distâncias com infinito e define o nó inicial com custo zero.
3. **Execução do Algoritmo**: Dispara o `solver.bmssp` com os parâmetros de nível (`level`) e limite (`bound`) extraídos do arquivo.
4. **Validação (Assertion)**: Compara o custo final no nó de destino com o valor esperado.
5. **Visualização**: Gera um mapa interativo `.html` para inspeção visual do resultado.

[Image of unit testing flowchart showing input json, process solver, and output html]

---

## 📂 Formato do Cenário (JSON)

Para que o teste funcione, o arquivo JSON em `/data` deve seguir esta estrutura:

```json
{
  "nodes": ["A", "B", "C"],
  "edges": [
    {"u": "A", "v": "B", "w": 10.5},
    {"u": "B", "v": "C", "w": 5.2}
  ],
  "test_params": {
    "start_node": "A",
    "target_node": "C",
    "level": 2,
    "bound": 20.0,
    "constants": {},
    "expected_cost": 15.7
  }
}