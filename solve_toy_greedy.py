import pickle
import repair_operators as ro
import matplotlib.pyplot as plt

from utils import plot_graph

if __name__ == "__main__":
    filename = "data/toys/toy_generated-1.pickle"
    graph = pickle.load(open(filename, "rb"))
    plot_graph(graph)
    plt.show()
    ro.greedy_initial_solution(graph)
