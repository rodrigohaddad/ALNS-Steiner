#%%
import networkx as nx
import alns.utils as utils
import alns.improvement as imp
from alns.solution_instance import SolutionInstance
from alns.simmulated_annealing import SimulatedAnnealing


file_name = "data/real_instances/cc3-5nu.stp"
G = utils.parse_instance(file_name)
nG = imp.remove_leaves(G)
print(f"nodes before preprocessing: {len(G)}")
print(f"nodes after preprocessing: {len(nG)}")
#utils.plot_graph(G, save=0)

def t_function_2(t: float, t0: float, beta=200) -> float:
    return t0 - beta * t

initial_solution = imp.greedy_initial_solution(nG)

params = {'temperature': 250,
            't_function': t_function_2,
            'alns_scores': [7, 3.5, 1, 0],
            'alns_decay': 0.8,
            'alns_n_iterations': 500}

origin_nodes = [n[0] for n in nG.nodes(data=True)]

initial_solution = SolutionInstance(nG, 
    initial_solution, instance_nodes=origin_nodes)

sa = SimulatedAnnealing(
    initial_solution=initial_solution, **params)

result = sa.simulate()
utils.plot_graph(nG, 
    solution=result['initial'].solution, save=0)
utils.plot_graph(nG, 
    solution=result['current'].solution, save=0)
utils.plot_graph(nG, 
    solution=result['best'].solution, save=0)
# %%
