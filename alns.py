class ALNS:
    def __init__(self):
        self._destroy_operators = []
        self._repair_operators = []

    def add_destroy_operator(self, operator):
        self._destroy_operators.append(operator)

    def add_repair_operator(self, operator):
        self._repair_operators.append(operator)

    def destroy_operators(self):
        return self._destroy_operators

    def repair_operators(self):
        return self._destroy_operators

    def iterate(self, curr_state):
        # logic
        return 0

