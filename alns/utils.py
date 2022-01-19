# %%
import re
import networkx as nx
import matplotlib.pyplot as plt

BEST = 0
BETTER = 1
ACCEPTED = 2
REJECTED = 3


def evaluate(state):
    return 0


def is_acceptable(state):
    return 0


def plot_graph(G: nx.Graph, output='plotgraph.png', terminals=True, solution=None) -> None:
    """
    Plots the given graph with its costs
    """
    plt.figure()
    labels = {g[:-1]:g[-1]["cost"]
        for g in G.edges(data=True)}

    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos=pos, with_labels=1)
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=labels)
    if solution is not None:
        nx.draw_networkx_edges(G, pos, edgelist=solution.edges(), edge_color='r', width=2)
    if terminals:
        terminals_n = [n for n, data in G.nodes(data=True) if data['terminal']]
        nx.draw_networkx_nodes(G, pos, nodelist=terminals_n, node_color='green')
    plt.savefig(output, dpi=200, bbox_inches='tight')


def parse_file(file_name: str) -> nx.Graph:
    """
    Parses a file with the following pattern:
    *garbage*
    'link'
    *line of grabage*
    int int int float\n
    int int int float\n
    .
    .
    .
    where int is a integer (e.g 10, 152) and 
    float is a float(e. g. 10.0, 15.2)
    """
    with open(file_name) as f:
        _text = f.read()

    #useful data starts a bit after here
    _text = _text.split("link")[-1]
    # switch white spaces for ';' (except new lines)
    text = re.sub(r'[^\S\r\n]+', ';', _text)
    
    # create graph
    G = nx.Graph()
    edge = []
    for line in text.split("\n")[2:]:
        for t in line.split(";"):
            if not t or t == "\n" or "#" in t: continue
            if len(edge) < 3:
                edge.append(int(t))
            else:
                edge.append(float(t))
                G.add_edge(edge[0], edge[1], 
                    cost=edge[2])
                edge = []


    return G


if __name__ == "__main__":
    # test_file = "data/steinc1-wmax_100-seed_33000-gw.dat"
    test_file = "data/test.edges"

    G = nx.Graph()
    G.add_edge('A', 'B', cost=4)
    G.add_edge('B', 'D', cost=2)
    G.add_edge('A', 'C', cost=3)
    G.add_edge('C', 'D', cost=4)
    plot_graph(G)

    G = parse_file(test_file)
    plot_graph(G)
# %%
