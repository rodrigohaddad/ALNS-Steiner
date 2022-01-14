import pickle
import repair_operators as ro

filename = "data/generated-pickle/toy_generated2.pickle"

graph = pickle.load( open( filename, "rb" ) )

ro.greedy_initial_solution(graph)


