import pyomo.environ as pyo
from pyomo.opt import SolverFactory


def solve(graph):
    """
    min cost_edge + prize_outter_nodes
    should be connected
    binary variables to choose the nodes
    binary variables to choose the edges
    """
    nodes = [0 for _ in range(len(graph))]
    n_prize = {}
    i = 0
    for n, n_data in graph.nodes(data=True):
        nodes[i] = n
        n_prize[n] = n_data['prize']
        i += 1

    edges = [i for i in range(len(graph.edges))]
    n1 = {}
    n2 = {}
    e_cost = {}
    i = 0
    for node1, node2, e_data in graph.edges(data=True):
        n1[i] = node1
        n2[i] = node2
        e_cost[i] = e_data['cost']
        i += 1

    model = pyo.ConcreteModel()
    
    # Define the sets to help creating variables and parameters
    model.nodes = pyo.Set(initialize=nodes, doc="Nodes")
    model.edges = pyo.Set(initialize=edges, doc="Edges")

    # Add the data to the problem
    model.prize = pyo.Param(model.nodes, initialize=n_prize, doc="Nodes prizes if taken (cost if not)")
    model.cost = pyo.Param(model.edges, initialize=e_cost, doc="Edges costs added if taken")
    model.n1 = pyo.Param(model.edges, initialize=n1, doc="One side of the edge")
    model.n2 = pyo.Param(model.edges, initialize=n2, doc="The other side of the edge")

    # Create the variables
    model.n = pyo.Var(model.nodes, domain=pyo.Binary, doc="Select nodes to the solution tree")
    model.e = pyo.Var(model.edges, domain=pyo.Binary, doc="Select edges to the solution tree")
    model.aux = pyo.Var(domain=pyo.NonNegativeIntegers)

    # Add the constraints (rules)
    def edge_rule(model, i):
        return 2 * model.e[i] <= model.n[model.n1[i]] + model.n[model.n2[i]]
    model.edge_rule = pyo.Constraint(model.edges, rule=edge_rule, doc="If one edge is added its nodes should be added")

    model.connective = pyo.Constraint(rule=sum(model.n[i] for i in model.nodes) == sum(model.e[i] for i in model.edges) + 1)

    def node_rule(model, i):
        return model.n[i] <= model.e[model.n1.sparse_values().index(i)] + model.e[model.n2.sparse_values().index(i)]
    model.node_rule = pyo.Constraint(model.nodes, rule=node_rule)

    # Define the objective
    def objective(model):
        return pyo.sum_product(model.prize, model.n) - pyo.sum_product(model.cost, model.e)
    model.objective = pyo.Objective(rule=objective, sense=pyo.maximize, doc="Minimize cost")

    # Optimize it
    opt = SolverFactory('glpk')
    results = opt.solve(model)
    # #sends results to stdout
    results.write()
    # print("\nDisplaying Solution\n" + '-'*60)
    # pyomo_postprocess(None, model, results)

    return model





