# %%
import copy
import random
import networkx as nx

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


### Repair operators ###

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


def connect_pair(state: nx.Graph, total_graph: nx.Graph, 
        source: int, target: int) -> None:
    """This function modifies the state graph"""

    path = nx.dijkstra_path(total_graph, source, target, 'cost')
    for i, node in enumerate(path[1:], 1):
        prev_node = path[i-1]
        
        if not state.has_node(node):
            aux = {n:data for n, data in total_graph.nodes(data=True)}
            state.add_node(node, **aux[node]) # TODO: Verify if is adding the attributes
        
        if state.has_edge(prev_node, node):
            continue
        
        state.add_edge(prev_node, node, **total_graph[prev_node][node])


def random_repair(current: SolutionInstance) -> nx.Graph:
    """This function modifies the state graph"""

    state = current.solution
    total_graph = current.instance
    components = [
        state.subgraph(comp).copy() for comp in sorted(nx.connected_components(state), key=len, reverse=True) if
        len(comp) >= 2
    ]

    source_graph = components[0]
    for comp in components:
        source = random.choice(list(source_graph.nodes))
        target = random.choice(list(comp.nodes()))

        connect_pair(state, total_graph, source, target)

        source_graph = state.subgraph(
            max(nx.connected_components(state), key=len)
        )

    return state


def greedy_repair(current: SolutionInstance):
    # TODO: Ideia, ligar as componentes conexas utilizando o caminho mínimo entre elas se houver melhoria
    state = current.solution
    total_graph = current.instance


def regret_repair(state: nx.Graph, total_graph: nx.Graph):
    pass


### Destroy operators ###

degree_of_destruction = 0.25


def edges_to_remove(state: nx.Graph) -> int:
    return int(len(state.edges) * degree_of_destruction)


def random_removal(current: SolutionInstance, random_state) -> SolutionInstance:
    destroyed = current.solution.copy()
    to_be_destroyed = list(destroyed.edges)
    n_edges_to_remove = random_state.choice(len(to_be_destroyed),
                                            edges_to_remove(current.solution),
                                            replace=False)

    for e in n_edges_to_remove:
        destroyed.remove_edge(*to_be_destroyed[e])

    # Remove isolated nodes (with 0 degree)
    destroyed.remove_nodes_from(
        [node for node, degree in destroyed.degree 
            if degree == 0]
    )

    return SolutionInstance.new_solution_from_instance(current, destroyed)


def worst_removal(current: SolutionInstance, _) -> SolutionInstance:
    """ Removes the most expensive edges """
    destroyed = current.solution.copy()
    destroy_candidates = sorted(list(destroyed.edges(data=True)),
                                key=lambda tup: tup[2]['cost'],
                                reverse=True)

    for e in range(edges_to_remove(current.solution)):
        destroyed.remove_edge(*destroy_candidates[e][:2])

    # Remove isolated nodes (with 0 degree)
    destroyed.remove_nodes_from(
        [node for node, degree in 
            destroyed.degree if degree == 0]
    )

    return SolutionInstance.new_solution_from_instance(
        current, destroyed)


def shaw_removal(current: nx.Graph) -> nx.Graph:
    return current

# %%
