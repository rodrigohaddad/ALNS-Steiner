# %%
import re
import os
import pickle
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import alns.instance_generator.instance_generator as ig

from alns.utils import plot_graph
from alns.operators import repair_operators as ro

from typing import List, Tuple


def generate_multiple_instances(parameters:
        Tuple[int, int, int]) -> None:
    n = len(parameters)
    for i in range(1, n+1):
        num_nodes, num_terminals, num_edges = parameters[i-1]
        graph, _ = ig.generate_random_steiner(
            num_nodes=num_nodes, 
            num_terminals=num_terminals, 
            num_edges=num_edges
        )
        pickle.dump(graph, open(f"data/toys/toy_generated-{i}.pickle", "wb"))
        ig.export_to_dat(graph, f"data/toys/toy_generated-{i}.dat")
    
        solution = ro.greedy_initial_solution(graph)

        plot_graph(graph, output=f"data/toys/toy_generated-{i}.png", solution=solution)


def instances_to_excel() -> None:
    """
    Saves the toy instances into an excel file
    """
    def atoi(text):
        return int(text) if text.isdigit() else text
    def natural_keys(text):
        return [ atoi(c) for c in re.split('(\d+)',text) ]
    
    path = "data/toys/"
    file_names = [f"{path}{f}" 
        for f in os.listdir(path) if f.endswith(".pickle")]
    file_names.sort(key=natural_keys)
    
    graphs = []
    for file_name in file_names:
        with open(file_name, "rb") as p:
            graphs.append(pickle.load(p))

    graph_to_excel(graphs)


def graph_to_excel(Gs: List[nx.Graph]) -> None:
    """
    Converts a list of graphs into (urgh) excel
    """
    def node_to_df(G: nx.Graph) -> \
            Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Converts nodes info to a pandas dataframe
        """
        # this is ugly af
        node_info = { k:
            {"terminal":int(v["terminal"]), "prize":v["prize"], 
                "x":v["pos"][0], "y":v["pos"][1]}
            for k, v in G.nodes(data=True)}
        
        edges_info = { i:
            {"u": data[0], "v":data[1], 
                "cost": data[2]["cost"]}
            for i, data in enumerate(G.edges(data=True))}
        
        return (pd.DataFrame(node_info).T,
            pd.DataFrame( edges_info).T)

    dfs = list(map(node_to_df, Gs))

    def write_excel(dfs: List[pd.DataFrame], 
            filename: str, sheet_names: List[str]):
        """
        Writes the dataframe to excel
        """
        writer = pd.ExcelWriter(filename,
            engine='xlsxwriter')   
        
        for i, (mdfs, sheet_name) in enumerate(
                zip(dfs, sheet_names)):
            row = 0
            for df in mdfs:
                df.to_excel(writer, sheet_name=sheet_name,
                    startrow=row, startcol=0)   
                row = row + len(df.index) + 5
            
            worksheet = writer.sheets[sheet_name]
            img_name = f"data/toys/toy_generated-{i+1}.png"
            worksheet.insert_image("H4", img_name)
        
        writer.save()

    sheet_names = [f"BT{i+1}" for i in range(len(dfs))]
    write_excel(dfs, "instances_alns.xlsx", sheet_names)

    return dfs


if __name__ == "__main__":
    parameters = (
        # num_nodes, num_terminals, num_edges
        (10, 3, 10),
        (10, 4, 15),
        (10, 5, 20),
        (15, 5, 20),
        (15, 6, 25),
        (15, 7, 30),
        (20, 7, 30),
        (20, 8, 35),
        (20, 9, 40),
        (25, 9, 40),
        (25, 10, 45),
        (25, 11, 50),
    )
    generate_multiple_instances(parameters)
    instances_to_excel()


# %%
