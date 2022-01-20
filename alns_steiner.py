from alns.operators.repair_operators import greedy_initial_solution
from simmulated_annealing.simmulated_annealing import SimulatedAnnealing
from alns.utils import parse_file
from math import log
import pickle

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
    G = pickle.load(open("data/toys/toy_generated-1.pickle", "rb"))

    initial_solution = greedy_initial_solution(G)

    params = {'steps_per_temperature': 200,
              'temperature': 25000,
              't_function': t_function_2,
              'alns_weights': [4, 2.4, 3, 1.5],
              'alns_decay': 0.8,
              'alns_n_iterations': 100}

    origin_nodes = [n[0] for n in G.nodes(data=True)]

    sa = SimulatedAnnealing(origin_graph=G,
                            origin_nodes=origin_nodes,
                            initial_solution=initial_solution,
                            **params)
    sa.simulate()


if __name__ == "__main__":
    main()
