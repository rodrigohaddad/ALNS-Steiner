import os
import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def generate_random_steiner(
    num_nodes=10,
    num_edges=10,
    max_node_degree=10,
    min_prize=1,
    max_prize=100,
    num_terminals=5,
    min_edge_cost=1,
    max_edge_cost=10,
    cost_as_length=False,
    max_iter=100,
    seed=None
):
    """
    Produz uma instância prize collecting steiner de acordo
    com os parâmetros informados.

    Args:
        num_nodes - int, número de nós da instância
        num_edges - int, número máximo de arestas da instância
        max_node_degree - int, número máximo de conexões que um
            nó pode fazer (grau)
        min_prize - int, premiação mínima para os nós terminais
        max_prize - int, premiação máxima para os nós terminais
        num_terminals - int, número de terminais na instância
        min_edge_cost - int, custo mínimo da aresta
        max_edge_cost - int, custo máximo da aresta
        cost_as_lenght - booleano, se for verdadeiro, custo da aresta
            é definido pelo comprimento do arco, calculado como a
            distância euclidiana entre os pontos.
        max_iter - int, parâmetro interno para controlar número máximo
            de tentativas de geração de arcos de acordo com as regras
            do algoritmo (evita loops infinitos)

    Returns: Uma instância do problema prize collecting steiner na forma de
        Grafo (NetworkX) e uma tupla contendo a lista de nós (nodes),
        arestas (edges), a posição dos nós (position_matrix),
        o custo das arestas (edges_cost), a lista de terminais selecionados
        (terminals) e os prêmios para cada terminal selecionado (prizes).
    """

    if seed != None:
        np.random.seed(seed)

    # Inicializar Arrays
    # Contagem de Grau dos nós
    degree_count = np.zeros(num_nodes)

    # Probabilidade Inicial do Nó ser escolhido (1 - Grau) / Soma((1 - Grau))
    nodes = list(range(0, num_nodes))
    node_prob = (1 - degree_count) / (1 - degree_count).sum()

    # Lista de Arestas
    edges = []
    edges_cost = []

    # Gerar num_nodes pontos aleatórios no R²(0, 100)
    position_matrix = np.random.rand(2, num_nodes) * 100

    # Selecionar aleatoriamente num_terminals nós para serem terminais
    terminals = np.random.randint(0, num_nodes, size=num_terminals)

    # Gerar prêmios aleatórios para os nós terminais
    prizes = np.random.randint(min_prize, max_prize+1, size=num_terminals)

    # Geração das Arestas
    for e in range(num_edges):

        i = 0

        # Escolhe dois nós aleatoriamente com base na probabilidade de escolha
        u, v = np.random.choice(list(range(0, num_nodes)), 2, p=node_prob)

        # Verifica se os nós escolhidos são os mesmos, enquanto forem, v
        # será sorteado novamente
        while u == v or (u, v) in edges or (v, u) in edges or i < max_iter:
            u, v = np.random.choice(list(range(0, num_nodes)), 2, p=node_prob)
            i += 1

        # Garantidos u != v, deg(u) < max_degree, deg(v) < max_degree
        if (u, v) not in edges and (v, u) not in edges:

            # Adicionar as listas
            edges.append((u, v))

            # Adiciona à contagem de grau
            degree_count[u] += 1
            degree_count[v] += 1

            # Recalcula probabilidades
            node_prob = (1 - degree_count / degree_count.sum())
            node_prob = node_prob / node_prob.sum()

    # Gerar custos para arestas
    if cost_as_length:
        for edge in edges:
            u = np.array((position_matrix[0][edge[0]]),
                         position_matrix[1][edge[0]])
            v = np.array((position_matrix[0][edge[1]]),
                         position_matrix[1][edge[1]])

            euclidean_distance = np.linalg.norm(u-v)

            edges_cost.append(euclidean_distance)

    else:
        # Gerar custo aleatoriamente
        edges_cost = np.random.randint(
            min_edge_cost, max_edge_cost + 1, size=len(edges))

    # Criar grafo
    G = nx.Graph()

    # Cria Nós
    for node in nodes:
        if node in terminals:
            terminal_idx = np.where(terminals == node)
            G.add_node(
                node,
                pos=(position_matrix[0][node], position_matrix[1][node]),
                terminal=True,
                prize=prizes[terminal_idx][0]
            )

        else:
            G.add_node(
                node,
                pos=(position_matrix[0][node], position_matrix[1][node]),
                terminal=False,
                prize=0
            )

    # Cria arestas
    for j, edge in enumerate(edges):
        G.add_edge(edge[0], edge[1], cost=edges_cost[j])

    # Verifica se o grafo está completamente conectado
    graph_connected_components = sorted(nx.connected_components(G))

    # Se houver mais de um subgrafo desconectado
    if len(graph_connected_components) > 1:
        for subgraph in (graph_connected_components[1:]):

            # Seleciona o primeiro nó do subgrafo
            u = list(subgraph)[0]

            # Seleciona um nó qualquer do maior componente
            v = list(graph_connected_components[0])[
                random.randint(0, len(graph_connected_components[0])-1)]

            # Define aresta e custo
            edge = (u, v)

            if cost_as_length == True:
                cost = np.linalg.norm(
                    np.array([position_matrix[0][u], position_matrix[1][u]]) -
                    np.array(position_matrix[0][v], position_matrix[1][v])
                )
            else:
                cost = random.randint(min_edge_cost, max_edge_cost + 1)

            # Adiciona à lista fixa
            edges.append(edge)
            np.append(edges_cost, cost)

            # Cria aresta
            G.add_edge(u, v, cost=cost)

    return G, (nodes, edges, position_matrix, edges_cost, terminals, prizes)


def draw_steiner_graph(G):
    """
    Função básica para plotar o grafo da instância gerada

    Args:
        G - nx.Graph, instância do prize collecting steiner.

    Returns: Um plot da instância
    """

    # Posição dos Nós e Peso dos Nós
    node_pos = nx.get_node_attributes(G, 'pos')
    node_list = list(nx.get_node_attributes(G, 'prize').keys())
    node_size = [size if size > 1 else 50 for size in list(
        nx.get_node_attributes(G, 'prize').values())]

    # Define a figura
    f, ax = plt.subplots(figsize=(15, 15))

    # Plota os nós
    nx.draw_networkx_nodes(
        G,
        pos=node_pos,
        nodelist=node_list,
        node_size=node_size,
        ax=ax
    )

    # Plota arestas
    nx.draw_networkx_edges(
        G,
        pos=nx.get_node_attributes(G, 'pos'),
        edge_color='k',
        width=0.3,
        style='--',
        ax=ax
    )

def export_to_dat(graph, out):
    """

    Args:
        graph(nx.Graph): Instância do prize collecting steiner.
    """
    
    path = os.path.dirname(__file__)
    template = open(
        os.path.join(path, 'template.dat')
    ).read()

    nodes = []
    for n, data in graph.nodes(data=True):
        nodes.append(
            '\t'.join(['', f'{n}', '0.0', '0.0', f'{data["prize"]}'])
        )

    links = []
    i = 1
    for node1, node2, e_data in graph.edges(data=True):
        links.append(
            '\t'.join(['', f'{i}', f'{node1}', f'{node2}', f'{e_data["cost"]}', f'{data["prize"]}', '0.0'])
        )
        i += 1

    output = template.format(
        nodes = '\n'.join(nodes),
        links = '\n'.join(links),
    )

    with open(out, 'w') as  outfile:
        outfile.write(output)
