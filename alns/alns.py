import numpy as np
import numpy.random as rnd
from math import exp

import alns.utils as utils
from alns.operators import (random_removal, 
    worst_removal, random_repair, greedy_repair, terminals_repair)
from alns.solution_instance import SolutionInstance


class ALNS:

    def __init__(self, initial_solution: SolutionInstance,
                 statistics,
                 rnd_state=rnd.RandomState()):
        self.destroy_operators = [random_removal, worst_removal]
        self.repair_operators = [random_repair, greedy_repair, terminals_repair]
        self.curr_state = self.best = self.initial_solution = self.original_solution = initial_solution
        self.rnd_state = rnd_state
        self.statistics = statistics


    @staticmethod
    def choose_next_state_metropolis(metropolis: float,
                                     curr_state,
                                     candidate_state):
        if np.random.uniform() <= metropolis:
            return candidate_state, utils.ACCEPTED
        return curr_state, utils.REJECTED


    @staticmethod
    def metropolis(curr_state_eval: float, candidate_eval: float,
                   curr_temp: float) -> float:
        diff = candidate_eval - curr_state_eval
        met = min(exp(diff / curr_temp), 1)
        return met

    def select_random_index(self,
                            operators,
                            weights,
                            ):
        return self.rnd_state.choice(np.arange(0, len(operators)),
                                     p=weights / np.sum(weights))


    def decision_candidate(self, candidate, temp):
        met_value = self.metropolis(self.curr_state.value, candidate.value, temp)

        if candidate < self.best:
            self.curr_state = self.best = candidate
            weight = utils.BEST
        elif candidate < self.curr_state:
            self.curr_state = candidate
            weight = utils.BETTER
        else:
            self.curr_state, weight = self.choose_next_state_metropolis(met_value, self.curr_state, candidate)
        
        return weight


    def run(self,
            weights,
            operator_decay,
            temp,
            repair_weights,
            destroy_weights
            ):
        if not (repair_weights != [] or destroy_weights != []):
            repair_weights = np.ones(len(self.repair_operators), dtype=np.float16)
            destroy_weights = np.ones(len(self.destroy_operators), dtype=np.float16)

        r_index = self.select_random_index(self.repair_operators,
                                           repair_weights)
        r_op = self.repair_operators[r_index]

        d_index = self.select_random_index(self.destroy_operators,
                                           destroy_weights)
        d_op = self.destroy_operators[d_index]

        destroyed = d_op(self.curr_state, self.rnd_state)
        repaired = r_op(destroyed, self.curr_state)

        weight_index = self.decision_candidate(repaired, temp)

        destroy_weights[d_index] *= operator_decay
        destroy_weights[d_index] += (1 - operator_decay) * weights[weight_index]

        repair_weights[r_index] *= operator_decay
        repair_weights[r_index] += (1 - operator_decay) * weights[weight_index]

        self.statistics.add_evaluation_candidate_info(self.curr_state.value)
        self.statistics.add_evaluation_best_info(self.best.value)

        self.statistics.add_destroy_operator_info(d_op.__name__, weight_index)
        self.statistics.add_repair_operator_info(r_op.__name__, weight_index)

        return repair_weights, destroy_weights
