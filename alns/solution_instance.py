import networkx as nx


class SolutionInstance:
    """Object to represent an instance of the Steiner Problem with its solution and value."""

    def __init__(self, instance: nx.Graph, solution: nx.Graph, value=None, instance_nodes=None) -> None:
        self.__instance = instance
        self.__instance_nodes = instance_nodes
        self.__solution = solution
        self.__value = value
        if self.__instance_nodes is None:
            self.__instance_nodes = [n for n in instance.nodes]

    @staticmethod
    def evaluate(origin_graph: nx.Graph,
                 solution: nx.Graph, origin_nodes=None) -> int:
        if not origin_nodes:
            origin_nodes = [n for n in origin_graph.nodes]
        solution_n = [n for n in solution.nodes]
        unvisited_nodes = list(set(origin_nodes).difference(solution_n))

        cost_edges = sum([e[2]["cost"]
                          for e in solution.edges(data=True)])
        cost_unvisited_nodes = sum([origin_graph.nodes[n]['prize']
                                    for n in unvisited_nodes])

        return cost_edges + cost_unvisited_nodes

    @classmethod
    def new_solution_from_instance(cls, prev, solution):
        return cls(prev.instance, solution, None, prev.instance_nodes)

    def copy(self):
        return SolutionInstance(self.instance, self.solution.copy(), self.__value, self.instance_nodes)

    @property
    def instance(self):
        return self.__instance

    @property
    def instance_nodes(self):
        return self.__instance_nodes

    @property
    def value(self) -> int:
        if self.__value is None:
            self.__value = self.evaluate(self.__instance, self.__solution, self.__instance_nodes)
        return self.__value

    @property
    def solution(self) -> nx.Graph:
        return self.__solution

    def __lt__(self, other) -> bool:
        return self.value < other.value

    def __le__(self, other) -> bool:
        return self.value <= other.value

    def __gt__(self, other) -> bool:
        return self.value > other.value

    def __ge__(self, other) -> bool:
        return self.value >= other.value
