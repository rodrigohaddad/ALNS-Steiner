import networkx as nx
import random

from utils import plot_graph


def __is_already_visited(nc_sorted: list,
                         initial_solution: nx.Graph) -> int:
    for nc in nc_sorted:
        if nc[0] not in initial_solution.nodes():
            return nc[0]
    return 0


def greedy_initial_solution(path: nx.Graph) -> nx.Graph:
    """
       Returns a greedy initial solution for prize collecting.
       It visits the most expensive nodes in relation to its path cost
       and stops when the only possible next node was already visited.
    """
    initial_solution = nx.Graph()
    curr_node = (random.choice(list(path.nodes)))
    initial_solution.add_node(curr_node)
    while True:
        next_cost = {n: (n - e['weight']) for n, e in path[curr_node].items()}
        nc_sorted = sorted(next_cost.items(), key=lambda x: x[1], reverse=True)
        better_node = __is_already_visited(nc_sorted, initial_solution)
        if not better_node:
            break
        initial_solution.add_edge(curr_node, better_node, weight=path[curr_node][better_node]['weight'])
        curr_node = better_node

    plot_graph(initial_solution)
    return initial_solution


def greedy_repair():
    pass


def regret_repair():
    pass
