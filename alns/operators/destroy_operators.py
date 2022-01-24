import networkx as nx
from alns.solution_instance import SolutionInstance

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
        [node for node, degree in destroyed.degree if degree == 0]
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
        [node for node, degree in destroyed.degree if degree == 0]
    )

    return SolutionInstance.new_solution_from_instance(current, destroyed)


def shaw_removal(current: nx.Graph) -> nx.Graph:
    return current