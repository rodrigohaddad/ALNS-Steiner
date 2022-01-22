import networkx as nx
import random
from alns.utils import evaluate


def __is_already_visited(nc_sorted: dict,
                         initial_solution: nx.Graph) -> int:
    for nc, _ in nc_sorted.items():
        if nc not in initial_solution.nodes():
            return nc
    return -1


def greedy_initial_solution(path: nx.Graph,
                            max_tries: int = 500) -> nx.Graph:
    """
       Returns a greedy initial solution for prize collecting.
       It visits the most expensive nodes in relation to its path cost
       and stops when the only possible next node was already visited.
    """
    best_evaluation = 0
    terminals_n = [n for n, data in path.nodes(data=True) if data['terminal']]
    for _ in range(max_tries):
        for t in range(path.number_of_nodes()):
            candidate_solution = nx.Graph()
            curr_node = random.choice(terminals_n)
            candidate_solution.add_node(curr_node)
            while True:
                next_cost = {n: (n - e['cost'], path.nodes[n]['terminal']) for n, e in path[curr_node].items()}
                nc_sorted = dict(sorted(next_cost.items(), key=lambda x: x[1], reverse=True))
                better_node = __is_already_visited(nc_sorted, candidate_solution)
                if better_node == -1:
                    break
                candidate_solution.add_edge(curr_node,
                                            better_node,
                                            cost=path[curr_node][better_node]['cost'])
                curr_node = better_node

            if all(n in list(candidate_solution.nodes) for n in terminals_n):
                break
        candidate_eval = evaluate(path, candidate_solution)
        if not best_evaluation or candidate_eval < best_evaluation:
            best_evaluation = candidate_eval
            best_initial_solution = candidate_solution

    return best_initial_solution

def connect_pair(state: nx.Graph, total_graph: nx.Graph, source: int, target: int):
    # Warning: This function modifies the state graph
    path = nx.dijkstra_path(total_graph, source, target, 'cost')
    for i, node in enumerate(path[1:], 1):
        prev_node = path[i-1]
        if not state.has_node(node):
            aux = {n:data for n, data in total_graph.nodes(data=True)}
            state.add_node(node, **aux[node]) # TODO: Verify if is adding the attributes
        if state.has_edge(prev_node, node):
            continue
        state.add_edge(prev_node, node, **total_graph[prev_node][node])
    return state


def random_repair(state: nx.Graph, total_graph: nx.Graph):
    # Warning: This function modifies the state graph
    components = [
        state.subgraph(comp).copy() for comp in sorted(nx.connected_components(state), key=len, reverse=True) if len(comp) >= 2
    ]

    source_graph = components[0]
    for comp in components:
        source = random.choice(list(source_graph.nodes))
        target = random.choice(list(comp.nodes()))

        state = connect_pair(state, total_graph, source, target)

        source_graph = state.subgraph(
            max(nx.connected_components(state), key=len)
        )

    return state

def greedy_repair(state: nx.Graph, total_graph: nx.Graph):
    # TODO: Ideia, ligar as componentes conexas utilizando o caminho mínimo entre elas
    pass


def regret_repair(state: nx.Graph, total_graph: nx.Graph):
    pass
