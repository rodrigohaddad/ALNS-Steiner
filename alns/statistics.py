class Statistics:
    def __init__(self):
        self._evaluations_curr_state = list()
        self._evaluations_best = list()

        self._destroy_operator_counts = list()
        self._repair_operator_counts = list()

        self._destroy_operator_weights = list()
        self._repair_operator_weights = list()

        self._destroy_best_count = dict()
        self._repair_best_count = dict()

        self._temp_info = {'i': list(),
                           'temp_iter': list(),
                           'curr_temp': list()}

        self._iter = 0

        self._time_duration = 0

    def n_iterations(self):
        return self._iter

    def temp_info(self):
        return self._temp_info

    def time_duration(self):
        return self._time_duration

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

    def destroy_operator_n_improvements(self):
        return self._repair_best_count

    def repair_operator_n_improvements(self):
        return self._destroy_best_count

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

    def add_no_improvement(self, i, temp_iter, curr_temp):
        self._temp_info['i'].append(i)
        self._temp_info['temp_iter'].append(temp_iter)
        self._temp_info['curr_temp'].append(curr_temp)

    def add_time_duration(self, delta):
        self._time_duration = delta

    def add_improvement_repair_count_op(self, r_op):
        try:
            self._repair_best_count[r_op.name] += 1
        except:
            self._repair_best_count[r_op.name] = 1

    def add_improvement_destroy_count_op(self, d_op):
        try:
            self._destroy_best_count[d_op.name] += 1
        except:
            self._destroy_best_count[d_op.name] = 1
