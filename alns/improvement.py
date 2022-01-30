# %%
import copy
import random
import networkx as nx

from typing import Any, Dict, List, Tuple

from alns.solution_instance import SolutionInstance

Node = Tuple[int, Dict[str, Any]]
Edge = Tuple[int, int, Dict[str, int]]

degree_of_destruction = 0.25
evaluate = SolutionInstance.evaluate


### preprocess ###

def remove_leaves(G: nx.Graph) -> nx.Graph:
    """
    Remove graph leaves and returns the resulting graph
    as well as the nodes taken out
    """
    nG = copy.deepcopy(G)
    
    def _preprocess(nG: nx.Graph) -> None:
        nodes = [node
            for node in nG.nodes(data=True)
            if nG.degree(node[0])==1 and not node[1]["prize"]]
        if not nodes:
            return
    
        nG.remove_nodes_from([n[0] for n in nodes])
        _preprocess(nG)

    _preprocess(nG)
    return nG


def terminal_leaves(G: nx.Graph) -> Tuple[
        List[Node], List[Edge], nx.Graph]:
    """
    Merges terminal leaves into nodes. Assumes that
    the only leaves are terminals
    """
    nG = copy.deepcopy(G)
    
    def _preprocess(nG: nx.Graph)-> Tuple[
            List[Node], List[Edge], nx.Graph]:
        nodes = [node
            for node in nG.nodes(data=True)
            if nG.degree(node[0])==1]
        if not nodes:
            return ([], [])

        keep_nodes = []
        for node in nodes:
            # it only has one edge
            edge = list(nG.edges([node[0]], data=True))[0]
            linked_node = nG.nodes[edge[1]]

            # calculate reward for getting terminal
            add_prize = node[1]["prize"] - edge[-1]["cost"]
            # if the reward is positive we keep it
            if add_prize > 0:
                linked_node["prize"] += add_prize
                linked_node["terminal"] = True
                keep_nodes.append(node)

        edges = G.edges([n[0] for n in keep_nodes],
            data=True)
        nG.remove_nodes_from([n[0] for n in nodes])

        # return the nodes and edges to reconstruct graph
        nnodes, nedges = _preprocess(nG)
        return ((keep_nodes + nnodes), list(edges) + nedges)

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
