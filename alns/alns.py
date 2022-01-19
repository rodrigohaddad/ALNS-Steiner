import numpy as np
import numpy.random as rnd


class ALNS:
    def __init__(self, rnd_state=rnd.RandomState()):
        self.destroy_operators = []
        self.repair_operators = []
        self.rnd_state = rnd_state

    def add_destroy_operator(self, operator):
        self.destroy_operators.append(operator)

    def add_repair_operator(self, operator):
        self.repair_operators.append(operator)

    def select_random_index(self,
                            operators,
                            weights,
                            ):
        return self.rnd_state.choice(np.arange(0, len(operators)),
                                     p=weights / np.sum(weights))

    def decision_candidate(self, best, curr_state, repaired, criteria):

    def run(self,
            initial_solution,
            weights,
            operator_evaluation,
            operator_decay,
            criteria,
            iterations=10000):
        weights = np.asarray(weights, dtype=np.float16)
        curr_state = best = initial_solution
        repair_weights = np.ones(len(self.repair_operators), dtype=np.float16)
        destroy_weights = np.ones(len(self.destroy_operators), dtype=np.float16)

        for i in range(iterations):
            r_index = self.select_random_index(self.destroy_operators,
                                               repair_weights)
            r_op = self.repair_operators[r_index]

            d_index = self.select_random_index(self.repair_operators,
                                               destroy_weights)
            d_op = self.destroy_operators[d_index]

            destroyed = d_op(curr_state)
            repaired = r_op(destroyed)

            best, curr_state, weight_index = self.decision_candidate(best,
                                                                     curr_state,
                                                                     repaired,
                                                                     criteria)

            destroy_weights[d_index] *= operator_decay
            destroy_weights[d_index] += (1 - operator_decay) * weights[weight_index]

            repair_weights[r_index] *= operator_decay
            repair_weights[r_index] += (1 - operator_decay) * weights[weight_index]

        return best
