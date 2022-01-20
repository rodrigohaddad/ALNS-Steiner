import re
import networkx as nx
import matplotlib.pyplot as plt


BEST = 0
BETTER = 1
ACCEPTED = 2
REJECTED = 3


def evaluate(origin_graph: nx.Graph, solution: nx.Graph) -> int:
    origin_n = [n[0] for n in origin_graph.nodes(data=True)]
    solution_n = [n[0] for n in solution.nodes(data=True)]
    unvisited_nodes = list(set(origin_n).difference(solution_n))

    cost_edges = sum([e[2]["cost"]
                      for e in solution.edges(data=True)])
    cost_unvisited_nodes = sum([origin_graph.nodes[n]['prize']
                                for n in unvisited_nodes])

    return cost_edges + cost_unvisited_nodes


def is_acceptable(state):
    return True


def plot_graph(G: nx.Graph,
               output='plotgraph.png',
               terminals=True,
               solution=None) -> None:
    """
    Plots the given graph with its costs
    """
    plt.figure()
    labels = {g[:-1]: g[-1]["cost"]
              for g in G.edges(data=True)}

    node_labels = {
        node: data['prize'] for node, data in G.nodes(data=True)
    }

    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos=pos, labels=node_labels)
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=labels)
    if solution is not None:
        nx.draw_networkx_edges(G, pos,
            edgelist=solution.edges(), edge_color='r', width=2)
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

    # useful data starts a bit after here
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

