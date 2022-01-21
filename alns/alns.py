import numpy as np
import numpy.random as rnd
from math import exp

from alns import utils
from alns.operators.destroy_operators import random_removal


class ALNS:
    def __init__(self, origin_graph,
                 initial_solution,
                 origin_nodes,
                 rnd_state=rnd.RandomState()):
        self.destroy_operators = [random_removal]
        self.repair_operators = [random_removal]
        self.origin_graph = origin_graph
        self.origin_nodes = origin_nodes
        self.curr_state = self.best = self.initial_solution = initial_solution
        self.best_eval = utils.evaluate(self.origin_graph, self.curr_state, self.origin_nodes)
        self.rnd_state = rnd_state

    def select_random_index(self,
                            operators,
                            weights,
                            ):
        return self.rnd_state.choice(np.arange(0, len(operators)),
                                     p=weights / np.sum(weights))

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

    def decision_candidate(self, best, curr_state, candidate, temp):
        candidate_eval = utils.evaluate(self.origin_graph, candidate, self.origin_nodes)
        curr_state_eval = utils.evaluate(self.origin_graph, curr_state, self.origin_nodes)

        met_value = self.metropolis(curr_state_eval, candidate_eval, temp)

        if candidate_eval < self.best_eval:
            self.best_eval = candidate_eval
            return candidate, candidate, utils.BEST

        if candidate_eval < curr_state_eval:
            weight = utils.BETTER
        else:
            curr_state, weight = self.choose_next_state_metropolis(met_value,
                                                                   curr_state,
                                                                   candidate)
        return best, curr_state, weight

    def run(self,
            weights,
            operator_decay,
            temp,
            repair_weights,
            destroy_weights
            ):
        if not (repair_weights or destroy_weights):
            repair_weights = np.ones(len(self.repair_operators), dtype=np.float16)
            destroy_weights = np.ones(len(self.destroy_operators), dtype=np.float16)

        r_index = self.select_random_index(self.destroy_operators,
                                           repair_weights)
        r_op = self.repair_operators[r_index]

        d_index = self.select_random_index(self.repair_operators,
                                           destroy_weights)
        d_op = self.destroy_operators[d_index]

        destroyed = d_op(self.curr_state, self.rnd_state)
        repaired = r_op(destroyed, self.rnd_state)

        self.best, self.curr_state, weight_index = self.decision_candidate(self.best,
                                                                           self.curr_state,
                                                                           repaired,
                                                                           temp)

        destroy_weights[d_index] *= operator_decay
        destroy_weights[d_index] += (1 - operator_decay) * weights[weight_index]

        repair_weights[r_index] *= operator_decay
        repair_weights[r_index] += (1 - operator_decay) * weights[weight_index]

        return self.best, self.curr_state, repair_weights, destroy_weights
