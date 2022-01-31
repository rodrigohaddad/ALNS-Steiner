import os
from math import log
import pickle
from tkinter.tix import MAX
from matplotlib import pyplot as plt
from time import sleep, time
import threading

from alns import statistics, utils
import alns.improvement as imp
from alns.simmulated_annealing import SimulatedAnnealing
from alns.solution_instance import SolutionInstance


''' ALNS for Steiner prize collecting problem
An application of adaptive large neighborhood search
(ALNS) metaheuristics for Steiner prize collecting
problem optimization.'''


FILEPATH = 'data/toys'
RESULTPATH = 'data/results'
MAX_THREADS = 16


def t_function_1(t: float, t0: float, beta=0.9) -> float:
    return t0 * beta ** t


def t_function_2(t: float, t0: float, beta=200) -> float:
    return t0 - beta * t


def t_function_3(t: float, t0: float, a=1000, b=2000) -> float:
    return a / (log(t + b))


def _get_instances():
    for filename in os.listdir(FILEPATH):
        file = os.path.join(FILEPATH, filename)
        if not os.path.isfile(file):
            continue
        
        if file.endswith('pickle'):
            yield pickle.load(open(file, "rb")), filename

        elif file.endswith('stp'):
            yield utils.parse_instance(file), filename

        elif file.endswith('dat'):
            yield utils.parse_file(file), filename


def _process(G, filename, **params):
    results_list = []
    statistics_list = []
    timing_list = []

    for _ in range(5):
        t0 = time()
        initial_solution = SolutionInstance(G, imp.greedy_initial_solution(G))

        sa = SimulatedAnnealing(initial_solution=initial_solution, **params)
        result = sa.simulate()
        
        elapsed = time() - t0

        results_list.append(result)
        statistics_list.append(statistics_list)
        timing_list.append(elapsed)

    result_dict = {
        "results": results_list,
        "statistics": statistics_list,
        "timing": timing_list
    }

    result_filename = os.path.join(RESULTPATH, f'results-{filename}.pickle')
    with open(result_filename, 'wb') as result_file:
        pickle.dump(result_dict, result_file)


def _wait_threads(threads, limit=MAX_THREADS):
    while len(threads) >= limit:
        for i, t in enumerate(threads):
            if not t.is_alive():
                threads.pop(i)
        
        sleep(2)

def main():
    params = {'temperature': 250,
            't_function': t_function_2,
            'alns_scores': [7, 3.5, 1, 0],
            'alns_decay': 0.8,
            'alns_n_iterations': 500}

    threads = []
    for G, filename in _get_instances():

        G = imp.remove_leaves(G)

        if len(threads) >= MAX_THREADS:
            _wait_threads(threads)

        threads.append(
            threading.Thread(target=_process, args=(G, filename), kwargs=params)
        )

        threads[-1].start()

    _wait_threads(threads, limit=1)
        

if __name__ == "__main__":
    main()
