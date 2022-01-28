import random
import networkx as nx
from itertools import product
import numpy as np

from alns.solution_instance import SolutionInstance


class Operator:
    """Handles the random choice of the operator method to execute"""

    def __init_subclass__(cls, **kwargs):
        # Take the public methods
        cls.operators = [
            getattr(cls, m) for m in dir(cls)
            if callable(getattr(cls, m)) and m[0] != '_' and m not in dir(Operator)
        ]
        cls.num_operators = len(cls.operators)
        cls.weights = np.ones(cls.num_operators, dtype=np.float16) / cls.num_operators
        cls.range = np.arange(0, cls.num_operators)
        cls.count_operators = np.zeros(cls.num_operators, dtype=int)
        cls.score_operators = np.zeros(cls.num_operators, dtype=int)
        cls.index = None

    def update_weights(self, r=.8):
        for idx in range(self.num_operators):
            self.weights[idx] = (1 - r) * self.weights[idx] + r * (
                        self.score_operators[idx] / self.count_operators[idx])

        self.score_operators = np.zeros(self.num_operators, dtype=int)
        self.count_operators = np.zeros(self.num_operators, dtype=int)
        self.index = None

    def update_score(self, score):
        self.score_operators[self.index] += score
        self.count_operators[self.index] += 1

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
            prev_node = path[i - 1]

            if not state.has_node(node):
                aux = {n: data for n, data in current.instance.nodes(data=True)}
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
                cls.__connect_pair(temp, path[i - 1], path[i])
            if temp < previous:
                return temp
        return temp  # if no improvement in all possible pairs, act like random_repair

    @classmethod
    def terminals_repair(cls, current: SolutionInstance, previous: SolutionInstance, max_trials=5):
        # First connect the graph
        current = cls.greedy_repair(current, previous)

        terminals_n = [n for n, data in current.instance.nodes(data=True) if data['terminal']]

        for terminal in terminals_n:
            if terminal not in current.solution:
                temp = current.copy()
                list_temp = []
                for _ in range(max_trials):
                    cls.__connect_pair(temp, terminal, random.choice(list(temp.solution.nodes)))
                    list_temp.append(temp)
                    if temp < current:
                        break
                current = min(list_temp, key=lambda x: x.value)

        return current

    @classmethod
    def __regret_repair(cls, state: nx.Graph, total_graph: nx.Graph):
        pass


class DestroyOperator(Operator):
    DEGREE_OF_DESTRUCTION = 0.15

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
            connects_terminal_leaf = [current.instance.nodes(data=True)[to_be_destroyed[e][i]]['terminal']
                                      and current.instance.degree(to_be_destroyed[e][i]) == 1 for i in range(2)]
            if not any(connects_terminal_leaf):
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
        d_e = list(destroyed.edges(data=True))
        edges_profit = list()
        for n1, n2, cost in d_e:
            prize_n1 = current.instance.nodes(data=True)[n1]['prize']
            prize_n2 = current.instance.nodes(data=True)[n2]['prize']
            profit = max(prize_n1, prize_n2) - cost['cost']
            edges_profit.append((n1, n2, profit))

        destroy_candidates = sorted(edges_profit,
                                    key=lambda tup: tup[2],
                                    reverse=False)

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
