from alns.operators.repair_operators import greedy_initial_solution
from simmulated_annealing.simmulated_annealing import SimulatedAnnealing
from alns.utils import parse_file
from math import log

''' ALNS for Steiner prize collecting problem
An application of adaptive large neighborhood search
(ALNS) metaheuristics for Steiner prize collecting
problem optimization.'''


def t_function_1(t: float, t0: float, beta=0.9) -> float:
    return t0 * beta ** t


def t_function_2(t: float, t0: float, beta=0.3) -> float:
    return t0 - beta * t


def t_function_3(t: float, t0: float, a=2000, b=1000) -> float:
    return a / (log(t + b))


def main():
    G = parse_file("../data/test.edges")

    initial_state = greedy_initial_solution(G)

    params = {'steps': 5000,
              'temperature': 250000,
              't_function': t_function_3,
              'alns_weights': [4, 2.4, 3, 1.5],
              'alns_decay': 0.8,
              'alns_n_iterations': 20000}

    sa = SimulatedAnnealing(initial_state=initial_state,
                            **params)
    # sa.simulate()


if __name__ == "__main__":
    main()
