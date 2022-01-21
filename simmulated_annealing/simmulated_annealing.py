import numpy as np
import networkx as nx
from typing import Callable

from alns import utils
from alns.alns import ALNS


class SimulatedAnnealing:
    def __init__(self,
                 origin_graph: nx.Graph,
                 origin_nodes: list,
                 initial_solution: nx.Graph,
                 temperature: float,
                 t_function: Callable[[float, float], float],
                 alns_weights: list,
                 alns_decay: float,
                 alns_n_iterations: int,
                 ):
        self.temperature = temperature
        self.t_function = t_function
        self.origin_graph = origin_graph
        self.origin_nodes = origin_nodes
        self.initial_solution = initial_solution

        self.alns_weights = alns_weights
        self.alns_decay = alns_decay
        self.alns_n_iterations = alns_n_iterations

        self.alns = ALNS(self.origin_graph, self.initial_solution, self.origin_nodes)

    def apply_alns(self, temp, weights, repair_weights, destroy_weights):
        return self.alns.run(weights,
                             self.alns_decay,
                             temp,
                             repair_weights,
                             destroy_weights)

    def simulate(self) -> list:
        best = self.initial_solution
        best_eval = utils.evaluate(self.origin_graph, best, self.origin_nodes)
        curr_state, curr_state_eval = best, best_eval

        list_temps = list()
        repair_weights = list()
        destroy_weights = list()

        weights = np.asarray(self.alns_weights, dtype=np.float16)
        curr_temp = self.t_function(0, self.temperature)

        temp_iter = 0
        while curr_temp > 0.001:
            for i in range(self.alns_n_iterations):
                best, curr_state, repair_weights, destroy_weights = self.apply_alns(curr_temp,
                                                                                    weights,
                                                                                    repair_weights,
                                                                                    destroy_weights)

            curr_temp = self.t_function(temp_iter, self.temperature)
            list_temps.append(curr_temp)
            temp_iter += 1

        print(curr_state, curr_temp)
        return [best, best_eval, list_temps]
