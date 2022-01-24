from collections import defaultdict


class Statistics:
    def __init__(self):
        self._evaluations_candidate = list()
        self._evaluations_best = list()
        self._destroy_operator_counts = defaultdict(lambda: [0, 0, 0, 0])
        self._repair_operator_counts = defaultdict(lambda: [0, 0, 0, 0])

    def add_evaluation_candidate_info(self, evaluation):
        self._evaluations_candidate.append(evaluation)

    def add_evaluation_best_info(self, evaluation):
        self._evaluations_best.append(evaluation)

    def add_destroy_operator_info(self, op_name, weight_idx):
        self._destroy_operator_counts[op_name][weight_idx] += 1

    def add_repair_operator_info(self, op_name, weight_idx):
        self._repair_operator_counts[op_name][weight_idx] += 1
