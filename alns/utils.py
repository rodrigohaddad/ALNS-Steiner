import re
import networkx as nx
import matplotlib.pyplot as plt

from typing import Any, Dict

BEST = 0
BETTER = 1
ACCEPTED = 2
REJECTED = 3


def plot_graph(G: nx.Graph,
               output='plotgraph.png',
               terminals=True,
               solution=None,
               save=True,
               pos=None,
               title='Plot Graph',
               show=False) -> None:
    """
    Plots the given graph with its costs
    """
    plt.close('all')

    fig, (sub1, sub2) = plt.subplots(ncols=2)
    fig.suptitle(title)
    labels = {g[:-1]: g[-1]["cost"]
              for g in G.edges(data=True)}

    node_labels = {
        node: data['prize'] if data['prize'] != 0 else '' for node, data in G.nodes(data=True)
    }

    pos = pos or nx.spring_layout(G, weight='cost', k=1/len(G), iterations=200)
    nx.draw_networkx(G, pos=pos, labels=node_labels, node_size=100, ax=sub1)
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=labels, ax=sub1)

    if solution is not None:
        nx.draw_networkx_edges(G, pos,
            edgelist=solution.edges(), edge_color='r', width=2, ax=sub1)
        nx.draw_networkx(solution, pos=pos, labels=node_labels, node_size=100, ax=sub2)
        labels = {g[:-1]: g[-1]["cost"]
            for g in solution.edges(data=True)}
        nx.draw_networkx_edge_labels(solution, pos=pos, edge_labels=labels, ax=sub2)
        nx.draw_networkx_edges(solution, pos,
            edgelist=solution.edges(), edge_color='r', width=2, ax=sub2)
    
    if terminals:
        terminals_n = [n for n, data in G.nodes(data=True) if data['terminal']]
        nx.draw_networkx_nodes(G, pos, nodelist=terminals_n, node_color='green', ax=sub1)
        nx.draw_networkx_nodes(solution, pos, nodelist=terminals_n, node_color='green', ax=sub2)

    if save:
        fig = plt.gcf()
        fig.set_size_inches((11, 8.5), forward=False)
        fig.savefig(output, dpi=500) # Change is over here

    if show:
        plt.show()

    return pos


def plot_evals(statistics):
    plt.plot(range(statistics.n_iterations()),
             statistics.curr_state_evaluations(), label="curr eval", linestyle="-.")
    plt.plot(range(statistics.n_iterations()),
             statistics.best_evaluations(), label="best eval", linestyle=":")
    plt.legend()


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


def parse_instance(file_name: str) -> nx.Graph:
    """
    Parses a benchmark file into a
    nx graph
    """
    with open(file_name) as f:
        text = f.read()

    def get_sections(text: str) -> Dict[str, Any]:
        """
        Returns each section in the file
        """
        lines = text.split("\n")
        sections = {}
        c_section = {}
        started = False
        for line in lines:
            # start of new section
            if "SECTION" in line:
                title = line[len("SECTION")+1:]
                c_section[title] = []
                started = True
            # end of section
            elif "END" in line:
                sections.update(c_section)
                c_section = {}
                started = False
            # start parsing
            elif started:
                c_section[title].append(line)
        return sections

    sections = get_sections(text)

    def get_graph(sections: Dict[str, Any]) -> nx.Graph:
        graph = sections["Graph"][2:]

        G = nx.Graph()
        for _edge in graph:
            edge = _edge.split(" ")
            G.add_edge(int(edge[1]), int(edge[2]), 
                cost=float(edge[3]))
        return G

    G = get_graph(sections)

    def set_attrs(G: nx.Graph, sections: Dict[str, Any]) ->\
            Dict[str, Any]:
        terminals = [section.split(" ") 
            for section in sections["Terminals"][1:]]
        terminal_nodes = {int(terminal[1]):float(terminal[2])
            for terminal in terminals}

        attrs = {}
        for node in G.nodes:
            prize = terminal_nodes.get(node, 0)
            attrs[node] = {
                "terminal": bool(prize), 
                "prize": prize
            }

        nx.set_node_attributes(G, attrs)

    set_attrs(G, sections)
    
    return G