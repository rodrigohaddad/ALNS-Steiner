import numpy as np
import numpy.random as rnd
from math import exp

import alns.utils as utils
from alns.operators import DestroyOperator, RepairOperator
from alns.solution_instance import SolutionInstance


class ALNS:

    def __init__(self, initial_solution: SolutionInstance,
                 statistics,
                 rnd_state=rnd.RandomState()):
        self.destroy_operator = DestroyOperator()
        self.repair_operator = RepairOperator()
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


    def run(self, weights, operator_decay, temp):

        destroyed = self.destroy_operator(self.curr_state, self.rnd_state)
        repaired = self.repair_operator(destroyed, self.curr_state)

        weight_index = self.decision_candidate(repaired, temp)

        self.destroy_operator.update_weights(operator_decay, weights[weight_index])
        self.repair_operator.update_weights(operator_decay, weights[weight_index])

        self.statistics.add_evaluation_candidate_info(self.curr_state.value)
        self.statistics.add_evaluation_best_info(self.best.value)

        self.statistics.add_destroy_operator_info(self.destroy_operator.name, weight_index)
        self.statistics.add_repair_operator_info(self.repair_operator.name, weight_index)
