from math import exp
import numpy as np
import networkx as nx
from typing import Any, Callable, List

from alns import utils
from alns.alns import ALNS


class SimulatedAnnealing:
    def __init__(self,
                 origin_graph: nx.Graph,
                 initial_solution: nx.Graph,
                 steps: int,
                 temperature: float,
                 t_function: Callable[[float, float], float],
                 alns_weights: list,
                 alns_decay: float,
                 alns_n_iterations: int,
                 start=1,
                 ):
        self.start = start
        self.temperature = temperature
        self.t_function = t_function
        self.steps = steps
        self.origin_graph = origin_graph
        self.initial_solution = initial_solution
        self.list_evals = list()
        self.list_temps = list()
        self.state_evals = dict()

        self.alns_weights = alns_weights
        self.alns_decay = alns_decay
        self.alns_n_iterations = alns_n_iterations
        self.alns = ALNS(self.origin_graph, self.initial_solution)

    @staticmethod
    def choose_next_state_metropolis(metropolis: float,
                                     curr_state, candidate_state):
        if np.random.uniform() <= metropolis:
            return candidate_state
        return curr_state

    @staticmethod
    def metropolis(curr_state_eval: float, candidate_eval: float,
                   curr_temp: float) -> float:
        diff = candidate_eval - curr_state_eval
        met = min(exp(diff / curr_temp), 1)
        return met

    def apply_alns(self):
        candidate = self.alns.run(self.alns_weights,
                                  self.alns_decay,
                                  self.alns_n_iterations)
        return candidate

    def simulate(self) -> List[Any, Any, float, float]:
        best = self.initial_state
        best_eval = utils.evaluate(self.origin_graph, best)
        curr_state, curr_state_eval = best, best_eval

        curr_temp = self.t_function(0, self.temperature)
        self.list_temps.append(curr_temp)
        self.list_evals.append(best_eval)

        while curr_temp > 0.001:
            for i in range(self.start, self.steps):
                candidate = self.apply_alns()
                candidate_eval = utils.evaluate(self.origin_graph, candidate)
                # print(curr_state, curr_state_eval, i)

                if candidate_eval >= curr_state_eval:
                    best, best_eval = candidate, candidate_eval
                    curr_state, curr_state_eval = candidate, candidate_eval
                else:
                    metropolis = self.metropolis(curr_state_eval, candidate_eval, curr_temp)
                    curr_state = self.choose_next_state_metropolis(metropolis,
                                                                   curr_state,
                                                                   candidate)
            curr_temp = self.t_function(curr_temp, self.temperature)
            self.list_temps.append(curr_temp)
            self.list_evals.append(best_eval)

        print(curr_state, curr_temp)
        return [best, best_eval, self.list_temps, self.list_evals]
