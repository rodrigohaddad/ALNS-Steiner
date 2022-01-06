import networkx as nx


def greedy_repair(current):
    graph_of_paths = nx.Graph()
    for v, inner_d in current.nodes(data=True):
        print('v', v, 'id', inner_d)


def regret_repair():
    pass
