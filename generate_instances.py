import alns.instance_generator.instance_generator as ig
import matplotlib.pyplot as plt
import pickle
from alns.utils import plot_graph
from alns.operators import repair_operators as ro


def generate_multiple_instances(parameters):
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

