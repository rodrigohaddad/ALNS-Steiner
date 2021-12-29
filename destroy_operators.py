degree_of_destruction = 0.25


def edges_to_remove(state):
    return int(len(state.edges) * degree_of_destruction)


def random_removal(current, random_state):
    destroyed = current.copy()

    for idx in random_state.choice(len(destroyed.nodes),
                                   edges_to_remove(current),
                                   replace=False):
        del destroyed.edges[destroyed.nodes[idx]]

    return destroyed


def worst_removal(current):
    destroyed = current.copy()

    worst_edges = sorted([])

    for idx in range(edges_to_remove(current)):
        del destroyed.edges[worst_edges[-idx -1]]

    return destroyed


def shawn_removal(current):
    return current
