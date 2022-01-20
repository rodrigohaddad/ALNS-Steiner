import networkx as nx

degree_of_destruction = 0.25


def edges_to_remove(state: nx.Graph) -> int:
    return int(len(state.edges) * degree_of_destruction)


def random_removal(current: nx.Graph, random_state) -> nx.Graph:
    destroyed = current.copy()

    for idx in random_state.choice(len(destroyed.nodes),
                                   edges_to_remove(current),
                                   replace=False):
        del destroyed.edges[destroyed.nodes[idx]]

    return destroyed


def worst_removal(current: nx.Graph) -> nx.Graph:
    destroyed = current.copy()

    worst_edges = sorted([])

    for idx in range(edges_to_remove(current)):
        del destroyed.edges[worst_edges[-idx -1]]

    return destroyed


def shawn_removal(current: nx.Graph) -> nx.Graph:
    return current
