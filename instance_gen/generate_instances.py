import instance_generator as ig
import matplotlib.pyplot as plt
from utils import plot_graph
import pickle


def generate_multiple_instances(n=10):
    for i in range(1, n+1):
        graph, _ = ig.generate_random_steiner()
        pickle.dump(graph, open(f"data/toys/toy_generated-{i}.pickle", "wb"))


if __name__ == "__main__":
    generate_multiple_instances(n=10)
