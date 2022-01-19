import networkx as nx
import random
import matplotlib.pyplot as plt
from utils import plot_graph


def __is_already_visited(nc_sorted: dict,
                         initial_solution: nx.Graph) -> int:
    for nc, _ in nc_sorted.items():
        if nc not in initial_solution.nodes():
            return nc
    return -1


def greedy_initial_solution(path: nx.Graph, max_tries: int = 350) -> nx.Graph:
    """
       Returns a greedy initial solution for prize collecting.
       It visits the most expensive nodes in relation to its path cost
       and stops when the only possible next node was already visited.
    """
    terminals_n = [n for n, data in path.nodes(data=True) if data['terminal']]
    for t in range(max_tries):
        initial_solution = nx.Graph()
        curr_node = random.choice(terminals_n)
        initial_solution.add_node(curr_node)
        while True:
            next_cost = {n: (n - e['cost'], path.nodes[n]['terminal']) for n, e in path[curr_node].items()}
            nc_sorted = dict(sorted(next_cost.items(), key=lambda x: x[1], reverse=True))
            better_node = __is_already_visited(nc_sorted, initial_solution)
            if better_node == -1:
                break
            initial_solution.add_edge(curr_node,
                                      better_node,
                                      cost=path[curr_node][better_node]['cost'])
            curr_node = better_node

        if all(n in list(initial_solution.nodes) for n in terminals_n):
            break
    pos = plot_graph(path)
    nx.draw_networkx_edges(path, pos, edgelist=initial_solution.edges(), edge_color='r', width=2)
    nx.draw_networkx_nodes(path, pos, nodelist=terminals_n, node_color='green')
    plt.show()

    return initial_solution


def greedy_repair():
    pass


def regret_repair():
    pass
