import networkx as nx

degree_of_destruction = 0.25


def edges_to_remove(state: nx.Graph) -> int:
    return int(len(state.edges) * degree_of_destruction)


def random_removal(current: nx.Graph, random_state) -> nx.Graph:
    destroyed = current.copy()
    to_be_destroyed = list(destroyed.edges)
    n_edges_to_remove = random_state.choice(len(to_be_destroyed),
                                            edges_to_remove(current),
                                            replace=False)

    for e in n_edges_to_remove:
        destroyed.remove_edge(*to_be_destroyed[e])

    # Remove isolated nodes (with 0 degree)
    destroyed.remove_nodes_from(
        [node for node, degree in destroyed.degree if degree == 0]
    )

    return destroyed


def worst_removal(current: nx.Graph) -> nx.Graph:
    destroyed = current.copy()

    worst_edges = sorted([])

    for idx in range(edges_to_remove(current)):
        del destroyed.edges[worst_edges[-idx - 1]]

    return destroyed


def shawn_removal(current: nx.Graph) -> nx.Graph:
    return current
