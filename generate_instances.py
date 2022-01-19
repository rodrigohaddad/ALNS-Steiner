import alns.instance_generator.instance_generator as ig
import matplotlib.pyplot as plt
import pickle
from alns.utils import plot_graph
from alns.operators import repair_operators as ro


def generate_multiple_instances(n=10):
    for i in range(1, n+1):
        graph, _ = ig.generate_random_steiner()
        pickle.dump(graph, open(f"data/toys/toy_generated-{i}.pickle", "wb"))
        ig.export_to_dat(graph, f"data/toys/toy_generated-{i}.dat")
    
        solution = ro.greedy_initial_solution(graph)

        plot_graph(graph, output=f"data/toys/toy_generated-{i}.png", solution=solution)

if __name__ == "__main__":
    generate_multiple_instances(n=10)

