from alns import utils
from alns.improvement import greedy_initial_solution
from alns.simmulated_annealing import SimulatedAnnealing
from alns.solution_instance import SolutionInstance
from math import log
import pickle
from matplotlib import pyplot as plt


''' ALNS for Steiner prize collecting problem
An application of adaptive large neighborhood search
(ALNS) metaheuristics for Steiner prize collecting
problem optimization.'''


def t_function_1(t: float, t0: float, beta=0.9) -> float:
    return t0 * beta ** t


def t_function_2(t: float, t0: float, beta=200) -> float:
    return t0 - beta * t


def t_function_3(t: float, t0: float, a=1000, b=2000) -> float:
    return a / (log(t + b))


def main():
    # G = parse_file("data/test.edges")
    G = pickle.load(open("data/toys/toy_generated-4.pickle", "rb"))

    initial_solution = greedy_initial_solution(G)

    params = {'temperature': 250,
              't_function': t_function_2,
              'alns_scores': [7, 3.5, 1, 0],
              'alns_decay': 0.8,
              'alns_n_iterations': 500}

    origin_nodes = [n[0] for n in G.nodes(data=True)]

    initial_solution = SolutionInstance(G, initial_solution, instance_nodes=origin_nodes)

    sa = SimulatedAnnealing(initial_solution=initial_solution, **params)
    result = sa.simulate()
    utils.plot_graph(G, solution=result['initial'].solution)
    plt.show()
    utils.plot_graph(G, solution=result['current'].solution)
    plt.show()
    utils.plot_graph(G, solution=result['best'].solution)
    plt.show()


if __name__ == "__main__":
    main()
