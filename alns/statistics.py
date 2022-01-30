class Statistics:
    def __init__(self):
        self._evaluations_curr_state = list()
        self._evaluations_best = list()

        self._destroy_operator_counts = list()
        self._repair_operator_counts = list()

        self._destroy_operator_weights = list()
        self._repair_operator_weights = list()

        self._iter = 0

    def n_iterations(self):
        return self._iter

    def curr_state_evaluations(self):
        return self._evaluations_curr_state

    def best_evaluations(self):
        return self._evaluations_best

    def destroy_operator_counts(self):
        return self._destroy_operator_counts

    def repair_operator_counts(self):
        return self._repair_operator_counts

    def destroy_operator_weights(self):
        return self._destroy_operator_weights

    def repair_operator_weights(self):
        return self._repair_operator_weights

    def add_evaluation_info(self, alns):
        self._evaluations_best.append(alns.best.value)
        self._evaluations_curr_state.append(alns.curr_state.value)
        self._iter += 1

    def add_destroy_operator_info(self, op):
        self._destroy_operator_counts.append({n.__name__: c for n, c in zip(op.operators,
                                                                            op.count_operators)})
        self._destroy_operator_weights.append({n.__name__: w for n, w in zip(op.operators,
                                                                             op.weights)})

    def add_repair_operator_info(self, op):
        self._repair_operator_counts.append({n.__name__: c for n, c in zip(op.operators,
                                                                           op.count_operators)})
        self._repair_operator_weights.append({n.__name__: w for n, w in zip(op.operators,
                                                                            op.weights)})
