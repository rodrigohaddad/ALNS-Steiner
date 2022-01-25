# %%
import copy
import random
import networkx as nx
from itertools import product

from typing import Any, Dict, List, Tuple

from alns.solution_instance import SolutionInstance

Node = Tuple[int, Dict[Any, Any]]
Edge = Tuple[int, int, int]

degree_of_destruction = 0.25
evaluate = SolutionInstance.evaluate


### preprocess ###

def remove_leaves(G: nx.Graph) -> Tuple[Tuple[Node], 
        Tuple[Edge], nx.Graph]:
    """
    Remove graph leaves and returns the resulting graph
    as well as the nodes taken out
    """
    nG = copy.deepcopy(G)
    
    def _preprocess(nG: nx.Graph) -> Tuple[Node, Edge]:
        try:
            nodes, edges = zip(*[(node, edge) 
                for node, edge in zip(nG.nodes(data=True), 
                                      G.edges(data=True))
                    if nG.degree(node[0])==1])
        except ValueError:
            return ((), ())
    
        nG.remove_nodes_from([n[0] for n in nodes])
        nnodes, nedges = _preprocess(nG)
        return (nodes + nnodes, edges + nedges)

    return _preprocess(nG) + (nG,)


### Greedy Solution ###

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