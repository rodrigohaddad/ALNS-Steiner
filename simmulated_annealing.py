from math import exp
from random import choices
import numpy as np

from alns import ALNS


from typing import Any, Callable, List


class SimulatedAnnealing:
    def __init__(self,
                 initial_state,
                 steps: int,
                 temperature: float,
                 t_function: Callable[[float, float], float],
                 start=1):
        self.start = start
        self.temperature = temperature
        self.t_function = t_function
        self.steps = steps
        self.initial_state = initial_state
        self.list_evals = list()
        self.list_temps = list()
        self.state_evals = dict()

        self.alns = ALNS()

    def evaluate_state(self, candidate):
        # calculate route cost
        return 0

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

    def sort_state_candidate(self, curr_state):
        self.alns.iterate(curr_state)
        # apply ALNS
        return 0

    def simulate(self) -> List[Any, Any, float, float]:
        best = self.initial_state
        best_eval = self.evaluate_state(best)
        curr_state, curr_state_eval = best, best_eval

        curr_temp = self.t_function(0, self.temperature)
        self.list_temps.append(curr_temp)
        self.list_evals.append(best_eval)

        while curr_temp > 0.001:
            for i in range(self.start, self.steps):
                candidate = self.sort_state_candidate(curr_state)
                candidate_eval = self.evaluate_state(candidate)
                print(curr_state, curr_state_eval, i)

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
