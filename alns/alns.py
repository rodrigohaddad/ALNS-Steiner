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

    def decision_candidate(self, candidate, temp, count_no_improvement):
        met_value = self.metropolis(self.curr_state.value, candidate.value, temp)

        if candidate < self.best:
            self.curr_state = self.best = candidate
            score = utils.BEST
            count_no_improvement = 0
            self.statistics.add_improvement_repair_count_op(self.repair_operator)
            self.statistics.add_improvement_destroy_count_op(self.destroy_operator)
        elif candidate < self.curr_state:
            self.curr_state = candidate
            score = utils.BETTER
            count_no_improvement += 1
        else:
            self.curr_state, score = self.choose_next_state_metropolis(met_value, self.curr_state, candidate)
            count_no_improvement += 1

        return score, count_no_improvement

    def run(self, scores, temp, count_no_improvement):

        destroyed = self.destroy_operator(self.curr_state, self.rnd_state)
        repaired = self.repair_operator(destroyed, self.curr_state)

        score_idx, count_no_improvement = self.decision_candidate(repaired, temp, count_no_improvement)

        self.destroy_operator.update_score(scores[score_idx])
        self.repair_operator.update_score(scores[score_idx])

        return count_no_improvement
