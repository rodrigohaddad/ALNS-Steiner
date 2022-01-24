import numpy as np
from typing import Callable

from alns.alns import ALNS
from alns.solution_instance import SolutionInstance
from alns.statistics import Statistics


class SimulatedAnnealing:
    def __init__(self,
                 initial_solution: SolutionInstance,
                 temperature: float,
                 t_function: Callable[[float, float], float],
                 alns_weights: list,
                 alns_decay: float,
                 alns_n_iterations: int,
                 ):
        self.temperature = temperature
        self.t_function = t_function
        self.initial_solution = initial_solution

        self.statistics = Statistics()

        self.alns_weights = alns_weights
        self.alns_decay = alns_decay
        self.alns_n_iterations = alns_n_iterations

        self.alns = ALNS(self.initial_solution, self.statistics)

    def apply_alns(self, temp, weights, repair_weights, destroy_weights):
        return self.alns.run(weights,
                             self.alns_decay,
                             temp,
                             repair_weights,
                             destroy_weights)

    def simulate(self) -> dict:
        list_temps = list()
        repair_weights = list()
        destroy_weights = list()

        weights = np.asarray(self.alns_weights, dtype=np.float16)
        curr_temp = self.t_function(0, self.temperature)

        temp_iter = 0
        while curr_temp > 0.001:
            for i in range(self.alns_n_iterations):
                repair_weights, destroy_weights = self.apply_alns(curr_temp,
                                                                  weights,
                                                                  repair_weights,
                                                                  destroy_weights)

            curr_temp = self.t_function(temp_iter, self.temperature)
            list_temps.append(curr_temp)
            temp_iter += 1

        return {
            "initial": self.alns.initial_solution,
            "best": self.alns.best,
            "current": self.alns.curr_state,
            "statistics": self.statistics
        }
