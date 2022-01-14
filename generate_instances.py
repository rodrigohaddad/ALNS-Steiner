import instance_generator as ig
import matplotlib.pyplot as plt
from utils import plot_graph
import pickle

graph, _ = ig.generate_random_steiner()
plot_graph(graph)
plt.show()
pickle.dump(graph, open("toy_generated.pickle", "wb"))
