from repair_operators import greedy_repair, greedy_initial_solution
from simmulated_annealing import SimulatedAnnealing
from utils import parse_file
from math import log

''' ALNS for Steiner prize collecting problem
An application of adaptive large neighborhood search
(ALNS) metaheuristics for Steiner prize collecting
problem optimization.'''


def t_function_1(t, t0, beta=0.9):
    return t0 * beta ** t


def t_function_2(t, t0, beta=0.3):
    return t0 - beta * t


def t_function_3(t, t0, a=2000, b=1000):
    return a / (log(t + b))


def main():
    G = parse_file("data/test.edges")

    initial_state = greedy_initial_solution(G)

    params = {'steps': 5000,
              'temperature': 250000,
              't_function': t_function_3}

    sa = SimulatedAnnealing(initial_state=initial_state,
                            **params)
    # sa.simulate()


if __name__ == "__main__":
    main()
