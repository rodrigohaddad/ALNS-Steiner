import pickle
import matplotlib.pyplot as plt

from alns.operators.repair_operators import greedy_initial_solution
from alns.utils import plot_graph, evaluate


def main():
    filename = "data/toys/toy_generated-1.pickle"
    graph = pickle.load(open(filename, "rb"))
    initial_sol = greedy_initial_solution(graph)
    evaluation = evaluate(graph, initial_sol)
    plot_graph(graph, solution=initial_sol)
    plt.show()


if __name__ == "__main__":
    main()
