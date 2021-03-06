import numpy as np
from typing import Callable

from alns.alns import ALNS
from alns.solution_instance import SolutionInstance
from alns.statistics import Statistics
from datetime import datetime


class SimulatedAnnealing:
    def __init__(self,
                 initial_solution: SolutionInstance,
                 temperature: float,
                 t_function: Callable[[float, float], float],
                 alns_scores: list,
                 alns_decay: float,
                 alns_n_iterations: int,
                 ):
        self.temperature = temperature
        self.t_function = t_function
        self.initial_solution = initial_solution

        self.statistics = Statistics()

        self.alns_scores = alns_scores
        self.alns_decay = alns_decay
        self.alns_n_iterations = alns_n_iterations

        self.alns = ALNS(self.initial_solution, self.statistics)

    def apply_alns(self, temp, scores, count_no_improvement):
        return self.alns.run(scores,
                             temp,
                             count_no_improvement)

    def simulate(self) -> dict:
        list_temps = list()

        scores = np.asarray(self.alns_scores, dtype=np.float16)
        curr_temp = self.t_function(0, self.temperature)

        temp_iter = 0
        start_time = datetime.now()
        while temp_iter < 100: #curr_temp > 0.001:
            count_no_improvement = 0
            for i in range(self.alns_n_iterations):
                count_no_improvement = self.apply_alns(curr_temp,
                                                       scores,
                                                       count_no_improvement)
                if count_no_improvement >= 50:
                    self.statistics.add_no_improvement(i, temp_iter, curr_temp)
                    break

            curr_temp = self.t_function(temp_iter, self.temperature)
            list_temps.append(curr_temp)
            temp_iter += 1

            self.statistics.add_destroy_operator_info(self.alns.destroy_operator)
            self.statistics.add_repair_operator_info(self.alns.repair_operator)

            self.statistics.add_evaluation_info(self.alns)

            self.alns.destroy_operator.update_weights(self.alns_decay)
            self.alns.repair_operator.update_weights(self.alns_decay)

            # print(self.alns.destroy_operator.weights, self.alns.repair_operator.weights)

        end_time = datetime.now()
        self.statistics.add_time_duration(end_time-start_time)
        return {
            "initial": self.alns.initial_solution,
            "best": self.alns.best,
            "current": self.alns.curr_state,
            "statistics": self.statistics
        }
