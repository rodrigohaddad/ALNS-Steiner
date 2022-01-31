import csv
import random
from time import time
import networkx as nx
from itertools import product
import numpy as np
import math

from networkx import NetworkXError

from alns.solution_instance import SolutionInstance


class Operator:
    """Handles the random choice of the operator method to execute"""
    def __init__(self) -> None:
        self.weights = np.ones(self.num_operators, dtype=np.float16) / self.num_operators
        self.range = np.arange(0, self.num_operators)
        self.count_operators = np.zeros(self.num_operators, dtype=np.int)
        self.score_operators = np.zeros(self.num_operators, dtype=np.int)
        self.index = None
        self.time_dict = dict()        

    def __init_subclass__(cls, **kwargs):
        # Take the public methods
        cls.operators = [
            getattr(cls, m) for m in dir(cls)
            if callable(getattr(cls, m)) and m[0] != '_' and m not in dir(Operator)
        ]
        cls.num_operators = len(cls.operators)

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
        t1 = time()
        res = operator(*args)
        t2 = time()
        elapsed_time = t2 - t1
        if self.name in self.time_dict:
            self.time_dict[self.name].append(elapsed_time)
        else:
            self.time_dict[self.name] = [t2-t1]
        return operator(*args)

    @property
    def name(self):
        return self.operators[self.index].__name__

    def generate_table(self):
        header = ['Method', 'Total time', 'Number of runs', 'Average time']
        rows = []
        for method in self.time_dict.keys():
            time_list = self.time_dict[method]
            total_time = sum(time_list)
            number_of_runs = len(time_list)
            avg_time = total_time / number_of_runs
            rows.append([method, total_time, number_of_runs, avg_time])
        return header, rows

    def save_csv(self, csv_file=None):
        csv_file = csv_file or f"log_timer_{time()}.csv"
        header, rows = self.generate_table()
        print(f"Writing {csv_file}")
        with open(csv_file, 'w') as filename:
            writer = csv.writer(filename)
            writer.writerow(header)
            writer.writerows(rows)

    # def __del__(self):
    #     self.save_csv()


class RepairOperator(Operator):

    @staticmethod
    def __merge_path(current: SolutionInstance, path: list):
        state = current.solution

        for i, node in enumerate(path[1:], 1):
            prev_node = path[i - 1]

            if not state.has_node(node):
                aux = {n: data for n, data in current.instance.nodes(data=True)}
                state.add_node(node, **aux[node])

            if state.has_edge(prev_node, node):
                continue

            state.add_edge(prev_node, node, **current.instance[prev_node][node])

    @staticmethod
    def __connect_pair(current: SolutionInstance, source: int, target: int) -> None:
        """This function modifies the state graph"""

        path = nx.dijkstra_path(current.instance, source, target, 'cost')
        RepairOperator.__merge_path(current, path)

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
            target = random.choice(list(comp.nodes))

            cls.__connect_pair(current, source, target)

            source_graph = state.subgraph(
                max(nx.connected_components(state), key=len)
            )

        return current

    @classmethod
    def _greedy_repair(cls, current: SolutionInstance, previous: SolutionInstance):

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
    def greedy_repair_single_source(cls, current: SolutionInstance, previous: SolutionInstance):

        state = current.solution

        components = [
            state.subgraph(comp).copy() for comp in sorted(nx.connected_components(state), key=len, reverse=True) if
            len(comp) >= 2
        ]

        if len(components) <= 1:
            return current

        bigger_graph = components[0]
        for comp in components[1:]:
            source = random.choice(list(comp.nodes))

            cost, path = nx.single_source_dijkstra(current.instance, source, weight='cost')

            min_value = None
            min_node = None
            for key, value in cost.items():
                if key not in bigger_graph:
                    continue
                if min_value is None or value < min_value:
                    min_value = value
                    min_node = key

            cls.__merge_path(current, path[min_node])

            bigger_graph = state.subgraph(
                max(nx.connected_components(state), key=len)
            )

        return current

    @classmethod
    def terminals_repair(cls, current: SolutionInstance, previous: SolutionInstance, max_trials=5):
        # First connect the graph
        current = cls.greedy_repair_single_source(current, previous)

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

        not_terminal_leafs = list()
        for e in n_edges_to_remove:
            connects_terminal_leaf = [current.instance.nodes(data=True)[to_be_destroyed[e][i]]['terminal']
                                      and current.instance.degree(to_be_destroyed[e][i]) == 1 for i in range(2)]
            if not any(connects_terminal_leaf):
                not_terminal_leafs.append(to_be_destroyed[e])

        destroyed.remove_edges_from(not_terminal_leafs)

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

        to_be_destroyed_edges = list()
        for e in range(cls.__edges_to_remove(current.solution)):
            to_be_destroyed_edges.append(destroy_candidates[e])

        destroyed.remove_edges_from(to_be_destroyed_edges)

        # Remove isolated nodes (with 0 degree)
        destroyed.remove_nodes_from(
            [node for node, degree in
             destroyed.degree if degree == 0]
        )

        return SolutionInstance.new_solution_from_instance(
            current, destroyed)

    @classmethod
    def shaw_removal(cls, current: SolutionInstance, _) -> nx.Graph:
        destroyed = current.solution.copy()
        d_e = list(destroyed.edges(data=True))
        edges_profit = list()
        for n1, n2, cost in d_e:
            prize_n1 = current.instance.nodes(data=True)[n1]['prize']
            prize_n2 = current.instance.nodes(data=True)[n2]['prize']
            profit = prize_n1 + prize_n2 - cost['cost']
            edges_profit.append((n1, n2, profit))

        destroy_candidates = sorted(edges_profit,
                                    key=lambda tup: tup[2],
                                    reverse=False)
        similar_nodes = list()
        for idx in range(len(destroy_candidates) - 1):
            if math.isclose(destroy_candidates[idx][2],
                            destroy_candidates[idx + 1][2],
                            rel_tol=0.07):
                similar_nodes.append(destroy_candidates[idx][:2])
                similar_nodes.append(destroy_candidates[idx + 1][:2])

        if not similar_nodes:
            return SolutionInstance.new_solution_from_instance(
                current, destroyed)

        to_be_destroyed_edges = list()
        for idx in range(cls.__edges_to_remove(current.solution)):
            if not any([current.instance.nodes(data=True)[similar_nodes[idx][i]]['terminal']
                        and current.instance.degree(similar_nodes[idx][i]) == 1 for i in range(2)]):
                to_be_destroyed_edges.append(similar_nodes[idx])

        destroyed.remove_edges_from(to_be_destroyed_edges)

        # Remove isolated nodes (with 0 degree)
        destroyed.remove_nodes_from(
            [node for node, degree in
             destroyed.degree if degree == 0]
        )

        return SolutionInstance.new_solution_from_instance(
            current, destroyed)
