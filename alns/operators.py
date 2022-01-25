
import random
import networkx as nx
from itertools import product
import numpy as np

from alns.solution_instance import SolutionInstance


def remove_leaves(G: nx.Graph) -> nx.Graph:
    """
    Remove graph leaves and returns the resulting graph
    as well as the nodes taken out
    """
    nG = copy.deepcopy(G)
    
    def _preprocess(nG: nx.Graph) -> None:
        try:
            nodes, edges = zip(*[(node, edge) 
                for node, edge in zip(nG.nodes(data=True), 
                                      G.edges(data=True))
                    if nG.degree(node[0])==1 and not node[1]["prize"]])
        except ValueError:
            return
    
        nG.remove_nodes_from([n[0] for n in nodes])
        _preprocess(nG)

    _preprocess(nG)
    return nG


class Operator:
    """Handles the random choice of the operator method to execute"""

    def __init_subclass__(cls, **kwargs):
        # Take the public methods
        cls.operators = [
            getattr(cls, m) for m in dir(cls) 
            if callable(getattr(cls, m)) and m[0] != '_' and m not in dir(Operator)
        ]
        num_operators = len(cls.operators)
        cls.weights = np.ones(num_operators, dtype=np.float16) / num_operators
        cls.range = np.arange(0, num_operators)
        cls.index = None

    def update_weights(self, operator_decay, weight):
        self.weights[self.index] = self.weights[self.index] * operator_decay + weight * (1 - operator_decay)

    def __call__(self, *args):
        self.index = np.random.choice(self.range, p=self.weights / np.sum(self.weights))
        operator = self.operators[self.index]
        return operator(*args)

    @property
    def name(self):
        return self.operators[self.index].__name__


class RepairOperator(Operator):
    
    @staticmethod
    def __connect_pair(current: SolutionInstance, source: int, target: int) -> None:
        """This function modifies the state graph"""

        state = current.solution
        path = nx.dijkstra_path(current.instance, source, target, 'cost')
        for i, node in enumerate(path[1:], 1):
            prev_node = path[i-1]
            
            if not state.has_node(node):
                aux = {n:data for n, data in current.instance.nodes(data=True)}
                state.add_node(node, **aux[node])
            
            if state.has_edge(prev_node, node):
                continue
            
            state.add_edge(prev_node, node, **current.instance[prev_node][node])

    @classmethod
    def random_repair(cls, current: SolutionInstance, *args) -> nx.Graph:
        """This function modifies the current solution"""

        state = current.solution
        components = [
            state.subgraph(comp).copy() for comp in sorted(nx.connected_components(state), key=len, reverse=True) if
            len(comp) >= 2
        ]

        if len(components) <= 1:
            return current

        source_graph = components[0]
        for comp in components[1:]:
            source = random.choice(list(source_graph.nodes))
            target = random.choice(list(comp.nodes()))

            cls.__connect_pair(current, source, target)

            source_graph = state.subgraph(
                max(nx.connected_components(state), key=len)
            )

        return current

    @classmethod
    def greedy_repair(cls, current: SolutionInstance, previous: SolutionInstance):

        state = current.solution

        components = [
            state.subgraph(comp).copy() for comp in sorted(nx.connected_components(state), key=len, reverse=True) if
            len(comp) >= 2
        ]

        if len(components) <= 1:
            return current
        
        nodes_in_components = [[n for n in comp] for comp in components]
        for comp in nodes_in_components:
            random.shuffle(comp)
        path_list = product(*nodes_in_components)

        for path in path_list:
            temp = current.copy()
            for i in range(1, len(path)):
                cls.__connect_pair(temp, path[i-1], path[i])
            if temp < previous:
                return temp
        return temp # if no improvement in all possible pairs, act like random_repair

    @classmethod
    def terminals_repair(cls, current: SolutionInstance, previous: SolutionInstance, max_trials=5):
        # First connect the graph
        current = cls.greedy_repair(current, previous)

        terminals_n = [n for n, data in current.instance.nodes(data=True) if data['terminal']]

        for terminal in terminals_n:
            if terminal not in current.solution:
                temp = current.copy()
                for _ in range(max_trials):
                    cls.__connect_pair(temp, terminal, random.choice(list(temp.solution.nodes)))
                    if temp < current:
                        current = temp
                        break
        return current

    @classmethod
    def __regret_repair(cls, state: nx.Graph, total_graph: nx.Graph):
        pass


class DestroyOperator(Operator):
    DEGREE_OF_DESTRUCTION = 0.25

    @classmethod
    def __edges_to_remove(cls, state: nx.Graph) -> int:
        return int(len(state.edges) * cls.DEGREE_OF_DESTRUCTION)

    @classmethod
    def random_removal(cls, current: SolutionInstance, random_state) -> SolutionInstance:
        destroyed = current.solution.copy()
        to_be_destroyed = list(destroyed.edges)
        n_edges_to_remove = random_state.choice(len(to_be_destroyed),
                                                cls.__edges_to_remove(current.solution),
                                                replace=False)

        for e in n_edges_to_remove:
            destroyed.remove_edge(*to_be_destroyed[e])

        # Remove isolated nodes (with 0 degree)
        destroyed.remove_nodes_from(
            [node for node, degree in destroyed.degree 
                if degree == 0]
        )

        return SolutionInstance.new_solution_from_instance(current, destroyed)

    @classmethod
    def worst_removal(cls, current: SolutionInstance, _) -> SolutionInstance:
        """ Removes the most expensive edges """
        destroyed = current.solution.copy()
        destroy_candidates = sorted(list(destroyed.edges(data=True)),
                                    key=lambda tup: tup[2]['cost'],
                                    reverse=True)

        for e in range(cls.__edges_to_remove(current.solution)):
            destroyed.remove_edge(*destroy_candidates[e][:2])

        # Remove isolated nodes (with 0 degree)
        destroyed.remove_nodes_from(
            [node for node, degree in 
                destroyed.degree if degree == 0]
        )

        return SolutionInstance.new_solution_from_instance(
            current, destroyed)

    @classmethod
    def __shaw_removal(cls, current: nx.Graph) -> nx.Graph:
        return current